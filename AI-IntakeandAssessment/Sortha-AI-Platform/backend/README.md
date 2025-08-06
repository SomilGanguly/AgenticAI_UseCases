# Sortha - backend
This is the backend part of the sortha platform.

## Folder Structure
```
📦backend
 ┃ ┣ 📂Models
 ┃ ┃ ┣ 📜File.py
 ┃ ┃ ┣ 📜Team.py
 ┃ ┃ ┗ 📜Workflow.py
 ┃ ┣ 📂Routers
 ┃ ┃ ┣ 📜Execution.py
 ┃ ┃ ┣ 📜File.py
 ┃ ┃ ┣ 📜Team.py
 ┃ ┃ ┣ 📜User.py
 ┃ ┃ ┗ 📜Workflow.py
 ┃ ┣ 📂Schemas
 ┃ ┃ ┣ 📜Execution.py
 ┃ ┃ ┣ 📜File.py
 ┃ ┃ ┣ 📜Folder.py
 ┃ ┃ ┣ 📜Team.py
 ┃ ┃ ┣ 📜User.py
 ┃ ┃ ┣ 📜UserTeam.py
 ┃ ┃ ┣ 📜Workflow.py
 ┃ ┃ ┣ 📜WorkflowRun.py
 ┃ ┃ ┗ 📜WorkFlowTeam.py
 ┃ ┣ 📂Services
 ┃ ┃ ┣ 📂FileService
 ┃ ┃ ┃ ┣ 📜FileService.py
 ┃ ┃ ┃ ┗ 📜LocalFileService.py
 ┃ ┃ ┣ 📂GlobalService
 ┃ ┃ ┃ ┗ 📜GlobalService.py
 ┃ ┃ ┣ 📂LogPipe
 ┃ ┃ ┃ ┗ 📜LogPipe.py
 ┃ ┃ ┗ 📂SorthaAI
 ┃ ┃ ┃ ┣ 📂AIClient
 ┃ ┃ ┃ ┃ ┗ 📜AzureChatOpenAI.py
 ┃ ┃ ┃ ┣ 📂Models
 ┃ ┃ ┃ ┃ ┗ 📜ExecutionState.py
 ┃ ┃ ┃ ┣ 📂pocs
 ┃ ┃ ┃ ┃ ┣ 📂TranscriptAwsToAzure
 ┃ ┃ ┃ ┃ ┃ ┣ 📜app.py
 ┃ ┃ ┃ ┃ ┃ ┣ 📜State.py
 ┃ ┃ ┃ ┃ ┃ ┗ 📜WorkFlow.py
 ┃ ┃ ┃ ┃ ┣ 📂TranscriptAwsToAzureExcel
 ┃ ┃ ┃ ┃ ┃ ┣ 📜app.py
 ┃ ┃ ┃ ┃ ┃ ┣ 📜State.py
 ┃ ┃ ┃ ┃ ┃ ┗ 📜WorkFlow.py
 ┃ ┃ ┃ ┃ ┣ 📂TranscriptAwsToAzureTF
 ┃ ┃ ┃ ┃ ┃ ┣ 📜app.py
 ┃ ┃ ┃ ┃ ┃ ┣ 📜FileWriterAgent.py
 ┃ ┃ ┃ ┃ ┃ ┣ 📜State.py
 ┃ ┃ ┃ ┃ ┃ ┣ 📜TerraformCodeParser.py
 ┃ ┃ ┃ ┃ ┃ ┗ 📜WorkFlow.py
 ┃ ┃ ┃ ┃ ┣ 📂TranscriptToAWSConfig
 ┃ ┃ ┃ ┃ ┃ ┣ 📜app.py
 ┃ ┃ ┃ ┃ ┃ ┣ 📜State.py
 ┃ ┃ ┃ ┃ ┃ ┗ 📜WorkFlow.py
 ┃ ┃ ┃ ┃ ┣ 📜test1.py
 ┃ ┃ ┃ ┃ ┗ 📜test2.py
 ┃ ┃ ┃ ┣ 📂WorkFlow
 ┃ ┃ ┃ ┃ ┗ 📜WorkFlowBase.py
 ┃ ┃ ┃ ┣ 📂WorkFlowExecution
 ┃ ┃ ┃ ┃ ┗ 📜WorkFlowExecution.py
 ┃ ┃ ┃ ┣ 📜main.py
 ┃ ┃ ┃ ┗ 📜SorthaAIService.py
 ┃ ┣ 📂Utils
 ┃ ┃ ┣ 📜DatabaseOps.py
 ┃ ┃ ┗ 📜Sortha.py
 ┃ ┣ 📂Workflows
 ┃ ┃ ┣ 📂TranscriptAwsToAzure
 ┃ ┃ ┃ ┣ 📜app.py
 ┃ ┃ ┃ ┣ 📜State.py
 ┃ ┃ ┃ ┗ 📜WorkFlow.py
 ┃ ┃ ┣ 📂TranscriptAwsToAzureExcel
 ┃ ┃ ┃ ┣ 📜app.py
 ┃ ┃ ┃ ┣ 📜State.py
 ┃ ┃ ┃ ┗ 📜WorkFlow.py
 ┃ ┃ ┣ 📂TranscriptAwsToAzureTF
 ┃ ┃ ┃ ┣ 📜app.py
 ┃ ┃ ┃ ┣ 📜FileWriterAgent.py
 ┃ ┃ ┃ ┣ 📜State.py
 ┃ ┃ ┃ ┣ 📜TerraformCodeParser.py
 ┃ ┃ ┃ ┗ 📜WorkFlow.py
 ┃ ┃ ┗ 📂TranscriptToAWSConfig
 ┃ ┃ ┃ ┣ 📜app.py
 ┃ ┃ ┃ ┣ 📜State.py
 ┃ ┃ ┃ ┗ 📜WorkFlow.py
 ┃ ┗ 📜initServices.py
 ┣ 📜database.py
 ┣ 📜dev.env
 ┣ 📜dev.env.activate.bat
 ┣ 📜dev.env.create.bat
 ┣ 📜dev.env.deactivate.bat
 ┣ 📜dev.env.pip.bat
 ┣ 📜dev.run.bat
 ┣ 📜dev_o4mini.env
 ┣ 📜main.py
 ┣ 📜prod.run.bat
 ┗ 📜requirements.txt
```
**Models:** It contains all the models for Request and Response object for the FastAPI server<br>
**Routers:** It contains all the different routes for API call for the FastAPI server<br>
**Schemas:** It defines all the tables and object view for SQLAlchemy ORM<br>
**Services:** It contains all the Services used by the Fast API deliver responses<br>
**Utils:** It contains all the various helper functions and classes<br>
**Workflows:** It will contain all the workflows available for consumption by the platform<br>

## Services
![Service Overview](/backend/docs/imgs/services.jpg)<br>
**FastAPIServer:** It is the API server providing functionality over REST APIs<br>
**SorthaAIService:** It is the AI backend responsible for running all the workflows<br>
**LogPipe Service:** It is the Logging Service<br>
**FileStorage Service:** It is the storage provider service. Responsible for processing the file for file IO<br>
**Global Service:** It is the Global Service Provider. It acts like a broker to provide all the services thoughout the life cycle of the program<br>

## Program Flow
![Program Flow Overview](/backend/docs/imgs/Program%20Flow.jpg)<br>
