from SorthaDevKit.StateBase import FileInputType, FileTypes

Input = {
    "transcript": FileInputType(
        file_path=r"C:\Users\smalisetty\OneDrive - Microsoft\Suchi\MSResearch\DeveloperToolkit\input\app_interview_transcript.txt",
        type=FileTypes.TEXT
    ),
    "questions_excel": FileInputType(
        file_path=r"C:\Users\smalisetty\OneDrive - Microsoft\Suchi\MSResearch\DeveloperToolkit\input\aif_unfilled.xlsx",
        type=FileTypes.EXCEL
    ),
    "azure_migrate_report": FileInputType(
        file_path=r"C:\Users\smalisetty\OneDrive - Microsoft\Suchi\MSResearch\DeveloperToolkit\input\azure_migrate_assessment.xlsx",
        type=FileTypes.EXCEL
    )
}

# Configuration for output
OUTPUT_CONFIG = {
    "output_file_path": r"C:\Users\smalisetty\OneDrive - Microsoft\Suchi\MSResearch\DeveloperToolkit\output\filled_aif.xlsx",
    "question_column_name": "Questions",  # Name of the column containing questions in Excel
    "excel_sheet_name": None,  # None to use first sheet, or specify sheet name
}
