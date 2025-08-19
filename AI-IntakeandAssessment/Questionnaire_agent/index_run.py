import argparse
try:
    from dotenv import load_dotenv; load_dotenv()
except Exception:
    pass
from indexer import index_container

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--app-id", required=True)
    p.add_argument("--container", required=True)
    args = p.parse_args()
    index_container(args.app_id, args.container)