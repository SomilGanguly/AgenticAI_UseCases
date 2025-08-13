# AI Root Cause Analysis (Azure OpenAI) Task

This task analyzes Azure Pipelines logs using Azure OpenAI to produce a concise root cause analysis and actionable fixes.

## Usage (YAML)
```yaml
- task: llm-rca-task@1
  inputs:
    azureOpenAiEndpoint: $(AZURE_OPENAI_ENDPOINT)
    azureOpenAiApiKey: $(AZURE_OPENAI_API_KEY)
    deploymentName: gpt-4o-mini
    logSource: auto # inline | file
    inlineLogs: ''
    logFilePath: ''
    maxChars: '40000'
    maxTokens: '1200'
    temperature: '0.2'
    outputFormat: markdown # text | json
    failOnHighSeverity: false
    allowUnsafeContent: false
```

Outputs are written to variables `LLMRCA.Markdown`, `LLMRCA.Json`, or `LLMRCA.Text` depending on format.

## Notes
- Provide a model deployment that supports Chat Completions in Azure OpenAI.
- To reduce token usage, prefer providing only the error section of logs.
- Secrets are redacted heuristically; review before enabling `allowUnsafeContent`.
