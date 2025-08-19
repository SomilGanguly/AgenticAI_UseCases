from dotenv import load_dotenv
load_dotenv()

import argparse
from pathlib import Path
from tools.xlsx_zip import materialize_clean_xlsx
from tools.blob import download_blob, upload_file
from agent import QuestionnaireAgent

def ask_user_console(q: str) -> str:
    print(f"Q: {q}")
    return input("Your answer (leave blank to skip): ")

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("--app-id", required=True)
    parser.add_argument("--container")  # optional when using local file
    parser.add_argument("--excel-blob")  # remote blob name
    parser.add_argument("--excel-path")  # local path for testing
    args = parser.parse_args()

    if args.excel_path:
        # Local test: materialize a clean workbook from the provided .xlsx
        src = Path(args.excel_path).expanduser().resolve()
        if not src.exists():
            raise FileNotFoundError(f"Local Excel not found: {src}")
        work_path = materialize_clean_xlsx(str(src))
        output_path = src.with_name(src.stem + ".out.xlsx")
        # Run agent on the clean copy
        agent = QuestionnaireAgent(args.app_id)
        def ask(prompt: str) -> str:
            print(f"\nQUESTION: {prompt}\nEnter answer (or leave blank to skip): ", end="")
            return input()
        agent.run(work_path, ask)
        # Save final workbook next to original
        Path(work_path).replace(output_path)
        print(f"Updated workbook written to: {output_path}")
        return

    # Blob path (existing behavior)
    if not (args.container and args.excel_blob):
        raise SystemExit("Provide either --excel-path for local test or both --container and --excel-blob for blob mode.")

    local_path = download_blob(args.container, args.excel_blob)
    work_path = materialize_clean_xlsx(local_path)  # robust read then clean write
    agent = QuestionnaireAgent(args.app_id)
    def ask(prompt: str) -> str:
        print(f"\nQUESTION: {prompt}\nEnter answer (or leave blank to skip): ", end="")
        return input()
    agent.run(work_path, ask)
    # Upload back to same blob name
    upload_file(args.container, work_path, dest_blob_name=args.excel_blob)

if __name__ == "__main__":
    run()