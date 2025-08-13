# LLM Root Cause Analysis Azure Pipelines Task

This Azure DevOps extension adds a pipeline task that analyzes error logs using Azure OpenAI and outputs:
- Root cause hypothesis
- Key failing steps/signals
- Suggested fixes and next actions
- Optional work item summary text

## Features
- Works on Linux, Windows, macOS agents (Node 20 handler)
- Accepts inline logs, a log file path, or auto-detects from `$(System.DefaultWorkingDirectory)`
- Connects to Azure OpenAI via API key or AAD (managed identity not supported in hosted agents)
- Supports GPT-4o/4.1/4.0-mini or compatible chat models
- Masks secrets and trims logs to fit model context
- Can fail the task if severity is high

## Quick Start
1. Set your extension `publisher` in `vss-extension.json`.
2. Package the extension:
   ```powershell
   npm install -g tfx-cli
   tfx extension create --manifest-globs vss-extension.json
   ```
3. Upload to your Azure DevOps organization marketplace and install.
4. Add task to your pipeline:
   ```yaml
   - task: llm-rca-task@1
     inputs:
       azureOpenAiEndpoint: $(AZURE_OPENAI_ENDPOINT)
       azureOpenAiApiKey: $(AZURE_OPENAI_API_KEY)
       deploymentName: gpt-4o-mini
       logSource: auto
       maxTokens: 1200
       temperature: 0.2
       outputFormat: markdown
       failOnHighSeverity: false
   ```

## Inputs
See `tasks/llm-rca/task.json` for details.

## Local Dev
- Node 20 LTS
- `npm ci` in `tasks/llm-rca`
- Run unit tests with `npm test` (coming soon)

## Security
- The task redacts obvious secrets via regex before sending to the LLM.
- Set `allowUnsafeContent: false` unless needed.

## License
MIT
