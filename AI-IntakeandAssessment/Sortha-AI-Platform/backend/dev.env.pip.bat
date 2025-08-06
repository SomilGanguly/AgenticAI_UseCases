@call venv\Scripts\activate.bat
pip %*
@pip freeze > requirements.txt
@echo Pip command executed and requirements.txt updated.