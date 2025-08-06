@call venv\Scripts\activate.bat
@echo Running in development mode...
@set ENV=dev
@python src/main.py %*
@echo Execution completed.