import * as tl from 'azure-pipelines-task-lib/task';
import axios from 'axios';
import * as fs from 'fs';

function redactSecrets(text: string, allowUnsafe: boolean): string {
  if (allowUnsafe) return text;
  const patterns: RegExp[] = [
    /(Authorization:\s*Bearer\s+)[A-Za-z0-9-_\.]+/gi,
    /(password|pwd|secret|token|apikey|api_key|access[_-]?key)\s*[:=]\s*[^\s\"']+/gi,
    /([A-Za-z0-9+\/=]{20,}\.[A-Za-z0-9+\/=]{10,}\.[A-Za-z0-9+\/=]{10,})/g // jwt-like
  ];
  let redacted = text;
  for (const p of patterns) {
    redacted = redacted.replace(p, '$1***REDACTED***');
  }
  return redacted;
}

function trimToMaxChars(text: string, maxChars: number): string {
  if (text.length <= maxChars) return text;
  // keep head and tail
  const half = Math.floor(maxChars / 2);
  return text.slice(0, half) + '\n...\n[truncated]\n...\n' + text.slice(-half);
}

function stripAnsi(str: string): string {
  return str.replace(/\u001b\[[0-9;]*m/g, '');
}

function buildDevOpsBaseUrl(orgInput: string): string {
  if (!orgInput) return '';
  const trimmed = orgInput.replace(/\/$/, '');
  if (/^https?:\/\//i.test(trimmed)) return trimmed;
  return `https://dev.azure.com/${trimmed}`;
}

function extractOrgFromCollectionUri(uri?: string): string | undefined {
  if (!uri) return undefined;
  try {
    const u = new URL(uri);
    // https://dev.azure.com/{org}/
    const parts = u.pathname.split('/').filter(Boolean);
    if (u.hostname.toLowerCase().includes('dev.azure.com') && parts.length >= 1) {
      return parts[0];
    }
    return uri.replace(/\/$/, ''); // fallback full URL
  } catch {
    return uri;
  }
}

async function fetchTimeline(org: string, project: string, buildId: string, patOrToken: string, useBearer: boolean) {
  const base = buildDevOpsBaseUrl(org);
  const url = `${base}/${encodeURIComponent(project)}/_apis/build/builds/${encodeURIComponent(buildId)}/timeline?api-version=5.1`;
  const authHeader = useBearer ? `Bearer ${patOrToken}` : 'Basic ' + Buffer.from(':' + patOrToken).toString('base64');
  try {
    const resp = await axios.get(url, { headers: { Authorization: authHeader } });
    const records = resp.data?.records;
    if (!Array.isArray(records)) throw new Error('Azure DevOps response did not contain an array of records.');
    return records;
  } catch (e: any) {
    const status = e?.response?.status;
    const msg = status ? `DevOps timeline request failed (${status}) for ${url}` : `DevOps timeline request failed for ${url}`;
    throw new Error(msg);
  }
}

async function fetchFullLogText(logUrl: string, patOrToken: string, useBearer: boolean): Promise<string> {
  const authHeader = useBearer ? `Bearer ${patOrToken}` : 'Basic ' + Buffer.from(':' + patOrToken).toString('base64');
  try {
    const resp = await axios.get(logUrl, { headers: { Authorization: authHeader } });
    let lines: string[] = [];
    if (typeof resp.data === 'string') {
      lines = resp.data.split('\n');
    } else if (Array.isArray(resp.data?.value)) {
      lines = resp.data.value;
    } else {
      throw new Error('Unsupported log format');
    }
    return lines.map(stripAnsi).join('\n');
  } catch (e: any) {
    const status = e?.response?.status;
    return `[Could not retrieve log: ${status || 'error'}]`;
  }
}

async function analyzeFailures(org: string, project: string, buildId: string, patOrToken: string, useBearer: boolean): Promise<string> {
  const records = await fetchTimeline(org, project, buildId, patOrToken, useBearer);
  let output = '';
  for (const record of records) {
    if (record.type === 'Task' && (record.result === 'failed' || record.result === 'canceled') && record.log) {
      output += `\n========================================\n`;
      output += `Failed Task   : ${record.name}\n`;
      output += `State         : ${record.state}\n`;
      output += `Result        : ${record.result}\n`;
      if (record.issues) {
        for (const issue of record.issues) {
          if (issue.type === 'error') {
            output += ` Error Message : ${issue.message}\n`;
          }
        }
      }
      try {
        const fullLog = await fetchFullLogText(record.log.url, patOrToken, useBearer);
        output += `\n--- Full Failed Task Log ---\n`;
        output += fullLog + '\n';
      } catch {
        output += `\n[Could not retrieve full log for ${record.name}]\n`;
      }
      output += `========================================\n`;
    }
  }
  return output || 'No failed task logs found.';
}

async function callOpenAI(endpoint: string, apiVersion: string, deployment: string, apiKey: string, content: string) {
  const url = `${endpoint.replace(/\/$/, '/') }openai/deployments/${encodeURIComponent(deployment)}/chat/completions?api-version=${encodeURIComponent(apiVersion)}`;
  const headers = { 'api-key': apiKey, 'Content-Type': 'application/json' };
  const body = {
    messages: [
      { role: 'system', content: 'You are a helpful assistant that analyzes Azure DevOps build failures and provides concise root cause and fixes.' },
      { role: 'user', content }
    ],
    temperature: 0.2
  };
  const resp = await axios.post(url, body, { headers });
  const text = resp.data?.choices?.[0]?.message?.content?.trim() || 'No response.';
  return text;
}

function logDebug(msg: string) {
  tl.debug(`[LLM-RCA] ${msg}`);
}

function mask(val?: string | null): string {
  if (!val) return '';
  if (val.length <= 6) return '***';
  return val.substring(0, 3) + '***' + val.substring(val.length - 3);
}

async function run() {
  try {
    logDebug('Task starting. Reading inputs.');
    const endpoint = tl.getInput('azureOpenAiEndpoint', true)!;
    const apiVersion = tl.getInput('azureOpenAiApiVersion', true)!;
    const deploymentName = tl.getInput('deploymentName', true)!;
    const apiKey = tl.getInput('azureOpenAiApiKey', false) || process.env.AZURE_OPENAI_API_KEY || '';
    const logSource = tl.getInput('logSource', true)!;
    const inlineLogs = tl.getInput('inlineLogs', false) || '';
    const logFilePath = tl.getInput('logFilePath', false) || '';
    const maxChars = parseInt(tl.getInput('maxChars', true)!, 10);
    const maxTokens = parseInt(tl.getInput('maxTokens', true)!, 10);
    const temperature = parseFloat(tl.getInput('temperature', true)!);
    const outputFormat = tl.getInput('outputFormat', true)! as 'markdown' | 'text' | 'json';
    const failOnHighSeverity = tl.getBoolInput('failOnHighSeverity', false);
    const allowUnsafeContent = tl.getBoolInput('allowUnsafeContent', false);

    logDebug(`Inputs summary: endpoint=${endpoint} apiVersion=${apiVersion} deployment=${deploymentName} logSource=${logSource} maxChars=${maxChars} maxTokens=${maxTokens} temp=${temperature} format=${outputFormat} failOnHighSeverity=${failOnHighSeverity} allowUnsafe=${allowUnsafeContent}`);
    logDebug(`API key (masked)=${mask(apiKey)}`);

    if (!apiKey) {
      logDebug('Missing API key. Failing early.');
      tl.setResult(tl.TaskResult.Failed, 'Azure OpenAI API key is required (input or AZURE_OPENAI_API_KEY env variable).');
      return;
    }

    let logs = '';
    if (logSource === 'build') {
      logDebug('Resolving build context from variables.');
      const inputOrg = tl.getInput('devopsOrg', false) || undefined;
      const inputProject = tl.getInput('devopsProject', false) || undefined;
      const inputBuildId = tl.getInput('buildId', false) || undefined;
      const inputPat = tl.getInput('devopsPat', false) || '';

      const sysCollectionUri = tl.getVariable('System.CollectionUri') || tl.getVariable('System.TeamFoundationCollectionUri');
      const sysProject = tl.getVariable('System.TeamProject');
      const sysBuildId = tl.getVariable('Build.BuildId');
      console.log({ buildId: sysBuildId });
      const sysAccessToken = tl.getVariable('System.AccessToken') || process.env.SYSTEM_ACCESSTOKEN || '';

      logDebug(`Auto vars: collectionUri=${sysCollectionUri} project=${sysProject} buildId=${sysBuildId} hasSystemAccessToken=${!!sysAccessToken}`);

      const orgAuto = inputOrg || extractOrgFromCollectionUri(sysCollectionUri);
      const projectAuto = inputProject || sysProject || '';
      const buildIdAuto = inputBuildId || sysBuildId || '';
      const useBearer = !inputPat && !!sysAccessToken;
      const credential = useBearer ? sysAccessToken : inputPat;

      logDebug(`Resolved build context: org=${orgAuto} project=${projectAuto} buildId=${buildIdAuto} authMode=${useBearer ? 'Bearer(System.AccessToken)' : (inputPat ? 'PAT' : 'NONE')}`);

      if (!orgAuto || !projectAuto || !buildIdAuto || !credential) {
        logDebug('Missing required DevOps context values after resolution.');
        tl.setResult(tl.TaskResult.Failed, 'Missing DevOps context. Ensure System.AccessToken is enabled or provide devopsPat, and that System.CollectionUri, System.TeamProject, Build.BuildId are available.');
        return;
      }
      try {
        logs = await analyzeFailures(orgAuto, projectAuto, buildIdAuto, credential, useBearer);
        logDebug(`Collected build failure log snippet length=${logs.length}`);
      } catch (e: any) {
        logDebug(`Error while fetching/analyzing build logs: ${e?.message}`);
        throw e;
      }
    } else if (logSource === 'inline') {
      logDebug('Using inline logs input.');
      logs = inlineLogs;
    } else if (logSource === 'file') {
      logDebug(`Reading logs from file: ${logFilePath}`);
      if (!fs.existsSync(logFilePath)) {
        logDebug('Specified log file not found.');
        tl.setResult(tl.TaskResult.Failed, `Log file not found: ${logFilePath}`);
        return;
      }
      logs = fs.readFileSync(logFilePath, 'utf8');
    } else {
      logDebug('Auto-detecting logs from default directories.');
      const defaultDir = tl.getVariable('System.DefaultWorkingDirectory') || process.cwd();
      const candidates = [
        `${defaultDir}/logs/agent.log`,
        `${defaultDir}/logs/build.log`,
        `${defaultDir}/_temp/diagnostics.log`
      ];
      for (const c of candidates) {
        if (fs.existsSync(c)) {
          logDebug(`Found candidate log file: ${c}`);
          logs = fs.readFileSync(c, 'utf8');
          break;
        }
      }
      if (!logs) {
        logDebug('No candidate log files found. Falling back to Agent.JobStatus variable.');
        logs = tl.getVariable('Agent.JobStatus') || 'No explicit log file provided. Include failing step logs in inline input for best results.';
      }
    }

    logDebug(`Raw logs length=${logs.length}`);

    const redacted = redactSecrets(logs, allowUnsafeContent);
    if (redacted !== logs) logDebug('Secrets redacted from logs.');

    const clipped = trimToMaxChars(redacted, isFinite(maxChars) ? maxChars : 40000);
    console.log(`clipped:${clipped}`);
    if (clipped.length !== redacted.length) logDebug(`Logs clipped to ${clipped.length} characters (maxChars=${maxChars}).`);

    const context = `Analyze the following Azure DevOps pipeline failure and suggest fixes. If possible, identify root cause, impacted steps, error signatures, and concrete actions.\n\n${clipped}`;

    logDebug('Invoking Azure OpenAI chat completion.');
    logDebug(`clipped: ${clipped}`);
    let text: string;
    try {
      text = await callOpenAI(endpoint, apiVersion, deploymentName, apiKey, context);
      logDebug(`Received response length=${text.length}`);
    } catch (e: any) {
      logDebug(`OpenAI request failed: ${e?.message}`);
      throw e;
    }

    let severity = 'medium';
    let output = text;
    if (outputFormat === 'json') {
      try { const parsed = JSON.parse(text); severity = parsed.severity || severity; logDebug(`Parsed JSON severity=${severity}`); } catch { logDebug('JSON parse failed – treating output as plain text.'); }
    } else if (output.toLowerCase().includes('severity: high')) { severity = 'high'; logDebug('Heuristic detected high severity in output.'); }

    if (outputFormat === 'markdown') tl.setVariable('LLMRCA.Markdown', output);
    else if (outputFormat === 'json') tl.setVariable('LLMRCA.Json', output);
    else tl.setVariable('LLMRCA.Text', output);
    logDebug('Output variable set.');

    console.log('\n===== AI Root Cause Analysis =====\n');
    console.log(output);

    if (failOnHighSeverity && severity === 'high') {
      logDebug('Failing task due to high severity and failOnHighSeverity=true.');
      tl.setResult(tl.TaskResult.Failed, 'High severity issue detected by AI analysis.');
      return;
    }

    tl.setResult(tl.TaskResult.Succeeded, 'AI analysis completed.');
    logDebug('Task succeeded.');
  } catch (err: any) {
    logDebug(`Unhandled error: ${err?.message || err}`);
    tl.setResult(tl.TaskResult.Failed, err?.message || String(err));
  }
}

run();
