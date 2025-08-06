@call venv\Scripts\activate.bat
@echo Running in development mode...
@set ENV=dev
@set ENV_PATH=./dev.env
@fastapi dev main.py --reload
@echo Execution completed.