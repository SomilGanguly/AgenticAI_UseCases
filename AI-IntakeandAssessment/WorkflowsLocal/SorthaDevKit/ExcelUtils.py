import pandas as pd
import openpyxl
from typing import List, Dict, Any
from .StateBase import QuestionAnswer, ExcelOutputType, AzureMigrateServer, AzureMigrateReport
import os
from datetime import datetime
import re

class ExcelProcessor:
    """Utility class for processing Excel files with questions and generating output Excel files."""
    
    @staticmethod
    def read_questions_from_excel(file_path: str, question_column: str = 'Questions', sheet_name: str = None) -> List[Dict[str, str]]:
        """
        Read questions from an Excel file with Questions, Category, and Priority columns.
        
        Args:
            file_path: Path to the Excel file
            question_column: Name of the column containing questions
            sheet_name: Name of the sheet to read (None for first sheet)
            
        Returns:
            List of dictionaries with question, category, and priority
        """
        try:
            # Determine which engine to use based on file extension
            # xlrd 2.0+ only supports .xls files, openpyxl handles .xlsx
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.xlsx':
                # For .xlsx files, use openpyxl engine
                engines = ['openpyxl']
            elif file_ext == '.xls':
                # For .xls files, use xlrd engine
                engines = ['xlrd']
            else:
                # For other extensions, try both
                engines = ['openpyxl', 'xlrd']
            
            df = None
            last_error = None
            
            for engine in engines:
                try:
                    if sheet_name:
                        df = pd.read_excel(file_path, sheet_name=sheet_name, engine=engine)
                    else:
                        df = pd.read_excel(file_path, engine=engine)
                    break  # Success, break out of loop
                except Exception as e:
                    last_error = e
                    continue
            
            if df is None:
                # If specific engines failed, try without specifying engine (let pandas decide)
                try:
                    if sheet_name:
                        df = pd.read_excel(file_path, sheet_name=sheet_name)
                    else:
                        df = pd.read_excel(file_path)
                except Exception as e:
                    raise Exception(f"Failed to read Excel file {file_path}. File extension: {file_ext}. Last error: {str(last_error)}")
            
            # Handle different possible column names for Questions
            possible_question_columns = [question_column, 'Questions', 'Question', 'questions', 'QUESTION']
            question_col = None
            
            for col in possible_question_columns:
                if col in df.columns:
                    question_col = col
                    break
            
            if question_col is None:
                question_col = df.columns[0]
            
            # Handle different possible column names for Category
            possible_category_columns = ['Category', 'category', 'CATEGORY', 'Categories']
            category_col = None
            
            for col in possible_category_columns:
                if col in df.columns:
                    category_col = col
                    break
            
            # Handle different possible column names for Priority
            possible_priority_columns = ['Priority', 'priority', 'PRIORITY', 'Priorities']
            priority_col = None
            
            for col in possible_priority_columns:
                if col in df.columns:
                    priority_col = col
                    break
            
            # Extract questions with their metadata
            questions_data = []
            for index, row in df.iterrows():
                question = str(row[question_col]).strip() if pd.notna(row[question_col]) else ""
                if question:  # Only add non-empty questions
                    category = str(row[category_col]).strip() if category_col and pd.notna(row[category_col]) else "General"
                    priority = str(row[priority_col]).strip() if priority_col and pd.notna(row[priority_col]) else "Medium"
                    
                    questions_data.append({
                        'question': question,
                        'category': category,
                        'priority': priority
                    })
            
            return questions_data
            
        except Exception as e:
            raise Exception(f"Error reading Excel file {file_path}: {str(e)}")
    
    @staticmethod
    def read_azure_migrate_report(file_path: str) -> AzureMigrateReport:
        """
        Read and parse Azure Migrate report from Excel file.
        
        Args:
            file_path: Path to the Azure Migrate Excel report
            
        Returns:
            AzureMigrateReport object with parsed data
        """
        try:
            # Determine which engine to use based on file extension
            # xlrd 2.0+ only supports .xls files, openpyxl handles .xlsx
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.xlsx':
                # For .xlsx files, use openpyxl engine
                engines = ['openpyxl']
            elif file_ext == '.xls':
                # For .xls files, use xlrd engine
                engines = ['xlrd']
            else:
                # For other extensions, try both
                engines = ['openpyxl', 'xlrd']
            
            excel_file = None
            last_error = None
            
            for engine in engines:
                try:
                    excel_file = pd.ExcelFile(file_path, engine=engine)
                    break
                except Exception as e:
                    last_error = e
                    continue
            
            if excel_file is None:
                try:
                    excel_file = pd.ExcelFile(file_path)
                except Exception as e:
                    raise Exception(f"Failed to read Excel file {file_path}. File extension: {file_ext}. Last error: {str(last_error)}")
            
            servers = []
            summary = {}
            metadata = {"source_file": file_path, "sheets_processed": []}
            
            # Process each sheet
            for sheet_name in excel_file.sheet_names:
                try:
                    df = pd.read_excel(file_path, sheet_name=sheet_name, engine=excel_file.engine)
                    metadata["sheets_processed"].append(sheet_name)
                    
                    # Try to identify server data sheets
                    if ExcelProcessor._is_server_data_sheet(df, sheet_name):
                        sheet_servers = ExcelProcessor._parse_server_sheet(df, sheet_name)
                        servers.extend(sheet_servers)
                    
                    # Try to identify summary sheets
                    elif ExcelProcessor._is_summary_sheet(df, sheet_name):
                        sheet_summary = ExcelProcessor._parse_summary_sheet(df, sheet_name)
                        summary.update(sheet_summary)
                        
                except Exception as e:
                    metadata[f"error_{sheet_name}"] = str(e)
                    continue
            
            return AzureMigrateReport(
                servers=servers,
                summary=summary,
                metadata=metadata
            )
            
        except Exception as e:
            raise Exception(f"Error reading Azure Migrate report {file_path}: {str(e)}")
    
    @staticmethod
    def _is_server_data_sheet(df: pd.DataFrame, sheet_name: str) -> bool:
        """Check if the sheet contains server/machine data."""
        sheet_name_lower = sheet_name.lower()
        
        # Specific Azure Migrate sheet names
        azure_migrate_machine_sheets = [
            'all assessed machines', 'assessed machines', 'machines', 
            'servers', 'vm assessment', 'server assessment'
        ]
        
        # Check for exact Azure Migrate sheet names
        if any(sheet_name_lower == indicator or indicator in sheet_name_lower 
               for indicator in azure_migrate_machine_sheets):
            return True
        
        # Check for general server indicators
        server_indicators = ['server', 'machine', 'vm', 'computer', 'host', 'node']
        if any(indicator in sheet_name_lower for indicator in server_indicators):
            return True
        
        # Check column headers for machine data indicators
        if len(df.columns) > 0:
            columns_str = ' '.join(df.columns.astype(str)).lower()
            column_indicators = [
                'server name', 'machine name', 'computer name', 'hostname', 
                'operating system', 'cpu', 'memory', 'disk', 'recommendation',
                'azure vm size', 'azure readiness', 'monthly cost estimate'
            ]
            if any(indicator in columns_str for indicator in column_indicators):
                return True
        
        return False
    
    @staticmethod
    def _is_summary_sheet(df: pd.DataFrame, sheet_name: str) -> bool:
        """Check if the sheet contains summary data."""
        sheet_name_lower = sheet_name.lower()
        
        # Specific Azure Migrate summary sheet names
        azure_migrate_summary_sheets = [
            'assessment summary', 'summary', 'overview', 'assessment properties'
        ]
        
        # Check for exact Azure Migrate sheet names
        if any(sheet_name_lower == indicator or indicator in sheet_name_lower 
               for indicator in azure_migrate_summary_sheets):
            return True
        
        # Check for general summary indicators
        summary_indicators = ['total', 'cost', 'recommendation', 'properties']
        return any(indicator in sheet_name_lower for indicator in summary_indicators)
    
    @staticmethod
    def _parse_server_sheet(df: pd.DataFrame, sheet_name: str) -> List[AzureMigrateServer]:
        """Parse server data from a sheet."""
        servers = []
        
        # Map common column variations to standard names (Azure Migrate specific)
        column_mapping = {
            'server_name': [
                'machine', 'server name', 'machine name', 'computer name', 'hostname', 'name', 'servername',
                'display name', 'vm name'
            ],
            'server_type': [
                'server type', 'machine type', 'type', 'servertype', 'operating system type',
                'platform', 'vm type', 'vm host'
            ],
            'operating_system': [
                'operating system', 'os', 'operatingsystem', 'platform', 'os name',
                'operating system name', 'os version'
            ],
            'cpu_cores': [
                'cores', 'cpu cores', 'processor cores', 'cpucores', 'vcpus', 'logical processors',
                'number of cores', 'core count', 'processors', 'processor'
            ],
            'memory_gb': [
                'memory(mb)', 'memory (mb)', 'memory(gb)', 'memory (gb)', 'memory', 'ram', 'ram (gb)', 'memory gb',
                'total memory', 'physical memory', 'memory size'
            ],
            'disk_size_gb': [
                'storage(gb)', 'storage (gb)', 'disk size (gb)', 'disk', 'storage', 'disk space', 'disk gb',
                'total disk size', 'storage size', 'disk capacity'
            ],
            'network_adapters': [
                'network adapters', 'nics', 'network cards', 'network interfaces',
                'ethernet adapters', 'network adapter count'
            ],
            'recommendation': [
                'recommended size', 'recommendation', 'azure recommendation', 'suggested sku', 'azure vm size',
                'recommended size', 'vm size recommendation', 'azure vm recommendation'
            ],
            'readiness': [
                'azure vm readiness', 'azure readiness', 'readiness', 'migration readiness', 'ready',
                'ready for azure', 'assessment status'
            ],
            'estimated_cost': [
                'compute monthly cost estimate usd', 'estimated cost', 'cost', 'monthly cost', 'cost estimate', 'monthly cost estimate',
                'azure cost', 'monthly cost (usd)', 'estimated monthly cost'
            ],
            'confidence': [
                'confidence rating (% of utilization data collected)', 'confidence', 'confidence rating', 'assessment confidence', 'rating confidence'
            ],
            'azure_vm_size': [
                'recommended size', 'azure vm size', 'vm size', 'recommended vm size', 'target vm size'
            ],
            'storage_type': [
                'storage type', 'disk type', 'recommended storage', 'azure storage type'
            ],
            'boot_type': [
                'boot type', 'boot', 'startup type'
            ],
            'cpu_usage': [
                'cpu usage(%)', 'cpu usage', 'processor usage', 'cpu utilization'
            ],
            'memory_usage': [
                'memory usage(%)', 'memory usage', 'ram usage', 'memory utilization'
            ]
        }
        
        # Find actual column names
        df_columns_lower = [col.lower().strip() for col in df.columns]
        mapped_columns = {}
        
        for standard_name, variations in column_mapping.items():
            for variation in variations:
                if variation in df_columns_lower:
                    mapped_columns[standard_name] = df.columns[df_columns_lower.index(variation)]
                    break
        
        # Process each row
        for _, row in df.iterrows():
            try:
                server = AzureMigrateServer()
                
                # Extract server information using mapped columns
                if 'server_name' in mapped_columns:
                    server.server_name = str(row[mapped_columns['server_name']]) if pd.notna(row[mapped_columns['server_name']]) else ""
                
                if 'server_type' in mapped_columns:
                    server.server_type = str(row[mapped_columns['server_type']]) if pd.notna(row[mapped_columns['server_type']]) else ""
                
                if 'operating_system' in mapped_columns:
                    server.operating_system = str(row[mapped_columns['operating_system']]) if pd.notna(row[mapped_columns['operating_system']]) else ""
                
                if 'cpu_cores' in mapped_columns:
                    try:
                        server.cpu_cores = int(float(str(row[mapped_columns['cpu_cores']]).replace(',', ''))) if pd.notna(row[mapped_columns['cpu_cores']]) else 0
                    except:
                        server.cpu_cores = 0
                
                if 'memory_gb' in mapped_columns:
                    try:
                        memory_val = str(row[mapped_columns['memory_gb']]).replace(',', '').replace('GB', '').replace('MB', '').strip()
                        server.memory_gb = float(memory_val) if memory_val else 0.0
                        # Convert MB to GB if needed
                        if 'mb' in mapped_columns['memory_gb'].lower():
                            server.memory_gb = server.memory_gb / 1024
                    except:
                        server.memory_gb = 0.0
                
                if 'disk_size_gb' in mapped_columns:
                    try:
                        disk_val = str(row[mapped_columns['disk_size_gb']]).replace(',', '').replace('GB', '').replace('TB', '').strip()
                        server.disk_size_gb = float(disk_val) if disk_val else 0.0
                        # Convert TB to GB if needed
                        if 'tb' in mapped_columns['disk_size_gb'].lower():
                            server.disk_size_gb = server.disk_size_gb * 1024
                    except:
                        server.disk_size_gb = 0.0
                
                if 'network_adapters' in mapped_columns:
                    try:
                        server.network_adapters = int(float(str(row[mapped_columns['network_adapters']]).replace(',', ''))) if pd.notna(row[mapped_columns['network_adapters']]) else 0
                    except:
                        server.network_adapters = 1  # Default to 1 NIC
                
                if 'recommendation' in mapped_columns:
                    server.recommendation = str(row[mapped_columns['recommendation']]) if pd.notna(row[mapped_columns['recommendation']]) else ""
                
                if 'readiness' in mapped_columns:
                    server.readiness = str(row[mapped_columns['readiness']]) if pd.notna(row[mapped_columns['readiness']]) else ""
                
                if 'estimated_cost' in mapped_columns:
                    try:
                        cost_val = str(row[mapped_columns['estimated_cost']]).replace('$', '').replace(',', '').strip()
                        server.estimated_cost = float(cost_val) if cost_val else 0.0
                    except:
                        server.estimated_cost = 0.0
                
                # Only add server if it has a valid name
                if server.server_name and server.server_name.lower() not in ['nan', 'none', '']:
                    servers.append(server)
                    
            except Exception as e:
                continue  # Skip invalid rows
        
        return servers
    
    @staticmethod
    def _parse_summary_sheet(df: pd.DataFrame, sheet_name: str) -> Dict[str, Any]:
        """Parse summary data from a sheet."""
        summary = {}
        
        try:
            # Try to extract key-value pairs from the summary sheet
            for _, row in df.iterrows():
                if len(row) >= 2:
                    key = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
                    value = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ""
                    
                    if key and value and key.lower() not in ['nan', 'none']:
                        summary[key] = value
            
            summary['source_sheet'] = sheet_name
            
        except Exception as e:
            summary['error'] = str(e)
        
        return summary
    
    @staticmethod
    def create_output_excel(excel_output: ExcelOutputType, output_path: str, original_questions_file: str = None):
        """
        Create an Excel file with questions, answers, and analysis matching the example structure.
        
        Args:
            excel_output: ExcelOutputType object with processed data
            output_path: Path where to save the output Excel file
            original_questions_file: Path to original questions file for reference
        """
        try:
            wb = openpyxl.Workbook()
            
            # Sheet 1: AI Assisted AIF Completion (matching example structure)
            ws_qa = wb.active
            ws_qa.title = "AI Assisted AIF Completion"
            
            # Headers matching the exact requirements (5 columns only)
            headers = ['Question', 'Answer', 'Confidence', 'Source Reference', 'Status']
            for col, header in enumerate(headers, 1):
                ws_qa.cell(row=1, column=col, value=header)
                ws_qa.cell(row=1, column=col).font = openpyxl.styles.Font(bold=True)
                # Add header background color
                ws_qa.cell(row=1, column=col).fill = openpyxl.styles.PatternFill(start_color="D3D3D3", end_color="D3D3D3", fill_type="solid")
            
            # Data rows
            for row, qa in enumerate(excel_output.questions_answers, 2):
                ws_qa.cell(row=row, column=1, value=qa.question)
                ws_qa.cell(row=row, column=2, value=qa.answer)
                ws_qa.cell(row=row, column=3, value=qa.confidence)
                ws_qa.cell(row=row, column=4, value=qa.source_reference)
                
                # Determine status more intelligently
                # Consider confidence, source reference, and answer content
                is_actually_answered = (
                    qa.is_answered and 
                    qa.confidence != "Unknown" and 
                    qa.source_reference not in ["N/A", "", "None", None] and
                    qa.answer not in ["Not addressed in transcript", "Error in analysis", "No answer provided", "Not found", ""]
                )
                
                ws_qa.cell(row=row, column=5, value="Answered" if is_actually_answered else "Not Answered")
                
                if qa.confidence == "High":
                    ws_qa.cell(row=row, column=3).fill = openpyxl.styles.PatternFill(start_color="90EE90", end_color="90EE90", fill_type="solid")
                elif qa.confidence == "Medium":
                    ws_qa.cell(row=row, column=3).fill = openpyxl.styles.PatternFill(start_color="FFFF99", end_color="FFFF99", fill_type="solid")
                elif qa.confidence == "Low":
                    ws_qa.cell(row=row, column=3).fill = openpyxl.styles.PatternFill(start_color="FFB6C1", end_color="FFB6C1", fill_type="solid")
                elif qa.confidence == "Unknown":
                    ws_qa.cell(row=row, column=3).fill = openpyxl.styles.PatternFill(start_color="E0E0E0", end_color="E0E0E0", fill_type="solid")
                
                # Color coding for status
                if is_actually_answered:
                    ws_qa.cell(row=row, column=5).fill = openpyxl.styles.PatternFill(start_color="90EE90", end_color="90EE90", fill_type="solid")
                else:
                    ws_qa.cell(row=row, column=5).fill = openpyxl.styles.PatternFill(start_color="FFB6C1", end_color="FFB6C1", fill_type="solid")
            
            # Sheet 2: Summary (matching example structure)
            ws_summary = wb.create_sheet(title="Summary")
            
            total_questions = len(excel_output.questions_answers)
            # Calculate actually answered questions using the same intelligent logic
            actually_answered_questions = len([
                qa for qa in excel_output.questions_answers 
                if (qa.is_answered and 
                    qa.confidence != "Unknown" and 
                    qa.source_reference not in ["N/A", "", "None", None] and
                    qa.answer not in ["Not addressed in transcript", "Error in analysis", "No answer provided", "Not found", ""])
            ])
            unanswered_questions = total_questions - actually_answered_questions
            
            # Summary data focusing on core metrics
            summary_data = [
                ["Total Questions", total_questions],
                ["Answered Questions", actually_answered_questions],
                ["Unanswered Questions", unanswered_questions],
                ["Answer Rate", f"{(actually_answered_questions/total_questions*100):.1f}%" if total_questions > 0 else "0%"],
                ["", ""],
                ["Confidence Distribution", ""],
                ["High Confidence", len([qa for qa in excel_output.questions_answers if qa.confidence == "High"])],
                ["Medium Confidence", len([qa for qa in excel_output.questions_answers if qa.confidence == "Medium"])],
                ["Low Confidence", len([qa for qa in excel_output.questions_answers if qa.confidence == "Low"])],
                ["Unknown Confidence", len([qa for qa in excel_output.questions_answers if qa.confidence == "Unknown"])],
                ["", ""],
                ["Generated On", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            ]
            
            for row, (label, value) in enumerate(summary_data, 1):
                ws_summary.cell(row=row, column=1, value=label)
                ws_summary.cell(row=row, column=2, value=value)
                if label and label != "":
                    ws_summary.cell(row=row, column=1).font = openpyxl.styles.Font(bold=True)
            
            # Sheet 3: Unanswered Questions (matching example structure)
            ws_unanswered = wb.create_sheet(title="Unanswered Questions")
            ws_unanswered.cell(row=1, column=1, value="Unanswered Questions")
            ws_unanswered.cell(row=1, column=1).font = openpyxl.styles.Font(bold=True)
            ws_unanswered.cell(row=1, column=1).fill = openpyxl.styles.PatternFill(start_color="D3D3D3", end_color="D3D3D3", fill_type="solid")
            
            unanswered_count = 2
            for qa in excel_output.questions_answers:
                # Use the same intelligent logic to determine if question is actually unanswered
                is_actually_answered = (
                    qa.is_answered and 
                    qa.confidence != "Unknown" and 
                    qa.source_reference not in ["N/A", "", "None", None] and
                    qa.answer not in ["Not addressed in transcript", "Error in analysis", "No answer provided", "Not found", ""]
                )
                if not is_actually_answered:
                    ws_unanswered.cell(row=unanswered_count, column=1, value=qa.question)
                    unanswered_count += 1
            
            # If no unanswered questions, add a message
            if unanswered_count == 2:
                ws_unanswered.cell(row=2, column=1, value="All questions have been answered!")
                ws_unanswered.cell(row=2, column=1).font = openpyxl.styles.Font(italic=True)
            
            for ws in wb.worksheets:
                for column in ws.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 80)  # Allow wider columns for questions
                    ws.column_dimensions[column_letter].width = adjusted_width
            
            wb.save(output_path)
            
        except Exception as e:
            raise Exception(f"Error creating output Excel file: {str(e)}")
    
    @staticmethod
    def validate_excel_file(file_path: str) -> bool:
        """
        Validate if the file is a valid Excel file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if valid Excel file, False otherwise
        """
        try:
            pd.read_excel(file_path, nrows=1)
            return True
        except:
            return False
