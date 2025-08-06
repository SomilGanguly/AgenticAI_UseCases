@call venv\Scripts\activate.bat
@echo Running in production mode...
@set ENV=dev
@set ENV_PATH=./dev.env
@fastapi run main.py
@echo Execution completed.