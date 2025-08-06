from dotenv import load_dotenv, find_dotenv
from os import getenv

# from pocs import test1
from pocs import test2
# from pocs.TranscriptToAWSConfig import app
# from pocs.TranscriptAwsToAzure import app
from pocs.TranscriptAwsToAzureTF import app

load_dotenv(find_dotenv(getenv('ENV_PATH', '../dev_o4mini.env')))

def main():
    app.main()
    # test2.main()

if __name__ == '__main__':
    main()