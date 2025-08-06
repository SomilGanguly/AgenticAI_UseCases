
from Workflows.LangGraphMigrationPlan import create_langgraph_workflow
from Input import Input
import sys
import logging
import os

# Set UTF-8 encoding for Windows console output
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Suppress HTTP request logging
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("azure").setLevel(logging.WARNING)

# Set environment variable to reduce Azure SDK verbosity
os.environ.setdefault("AZURE_LOG_LEVEL", "WARNING")

def main():
    print("SorthaDevKit - AI Assisted AIF filling and AMP Generation")
    print("=" * 40)
    
    # Create and run the LangGraph workflow
    workflow = create_langgraph_workflow(Input)
    result = workflow.run()
    
    if result.success:
        print("\n[SUCCESS] Complete migration plan generated successfully!")
        if hasattr(result, 'data') and result.data:
            print("Generated outputs:")
            if 'output_files' in result.data:
                output_files = result.data['output_files']
                if 'assessment_report' in output_files and output_files['assessment_report']:
                    print(f"  ✓ Application Assessment Report generated")
                if 'qa_report' in output_files and output_files['qa_report']:
                    print(f"  ✓ Q&A analysis report: output/filled_aif.xlsx")
                if 'migration_plans' in output_files and output_files['migration_plans']:
                    for file_type, file_path in output_files['migration_plans'].items():
                        if file_type != 'assessment_report':  # Avoid double-counting
                            print(f"  ✓ {file_type.title()} migration plan: {file_path}")
    else:
        print("\n[ERROR] Migration plan generation failed:")
        for error in result.errors:
            print(f"  - {error}")
    
    return result

if __name__ == "__main__":
    main()