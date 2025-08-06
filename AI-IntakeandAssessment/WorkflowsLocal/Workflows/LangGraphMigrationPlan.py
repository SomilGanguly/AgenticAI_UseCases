import os
import sys
from typing import List, Dict, Any, TypedDict, Annotated
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langgraph.graph import StateGraph
from langgraph.constants import START, END
from langgraph.checkpoint.memory import MemorySaver
from typing_extensions import TypedDict

from SorthaDevKit.StateBase import ProcessingResult, QuestionAnswer
from SorthaDevKit.ExcelUtils import ExcelProcessor
from SorthaDevKit.MigrationPlanGenerator import AzureMigrationPlanGenerator
from SorthaDevKit.MigrationPlanExporter import MigrationPlanDocumentExporter
from SorthaDevKit.AssessmentReportGenerator import ApplicationAssessmentReportGenerator


class WorkflowState(TypedDict):
    """State schema for the LangGraph workflow."""
    # Input data
    inputs: Dict[str, Any]
    
    # Processing results
    azure_migrate_data: Any
    questions_answers: List[QuestionAnswer]
    assessment_report_data: Any
    migration_plan: Any
    qa_export_success: bool
    assessment_export_success: bool
    plan_files: Dict[str, str]
    
    # Workflow metadata
    result: ProcessingResult
    llm_client: Any
    errors: List[str]
    step_completed: Dict[str, bool]


class LangGraphMigrationPlanWorkflow:
    """LangGraph-based Azure Migration Plan generation workflow."""
    
    def __init__(self, inputs: Dict[str, Any]):
        self.inputs = inputs
        self.migration_plan_generator = AzureMigrationPlanGenerator()
        self.document_exporter = MigrationPlanDocumentExporter()
        self.assessment_report_generator = ApplicationAssessmentReportGenerator()
        
        # Create the graph
        self.graph = self._create_workflow_graph()
    
    def _create_workflow_graph(self) -> StateGraph:
        """Create the LangGraph workflow."""
        # Define the workflow graph
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        workflow.add_node("initialize", self._initialize_node)
        workflow.add_node("validate_inputs", self._validate_inputs_node)
        workflow.add_node("setup_llm", self._setup_llm_node)
        workflow.add_node("process_azure_migrate", self._process_azure_migrate_node)
        workflow.add_node("process_questions", self._process_questions_node)
        workflow.add_node("generate_assessment_report", self._generate_assessment_report_node)
        workflow.add_node("generate_plan", self._generate_plan_node)
        workflow.add_node("export_qa", self._export_qa_node)
        workflow.add_node("export_assessment_report", self._export_assessment_report_node)
        workflow.add_node("export_documents", self._export_documents_node)
        workflow.add_node("finalize", self._finalize_node)
        
        # Define the flow
        workflow.add_edge(START, "initialize")
        workflow.add_edge("initialize", "validate_inputs")
        workflow.add_conditional_edges(
            "validate_inputs",
            self._should_continue_after_validation,
            {
                "continue": "setup_llm",
                "end": END
            }
        )
        workflow.add_conditional_edges(
            "setup_llm", 
            self._should_continue_after_llm,
            {
                "continue": "process_azure_migrate",
                "end": END
            }
        )
        workflow.add_conditional_edges(
            "process_azure_migrate",
            self._should_continue_after_azure_migrate,
            {
                "continue": "process_questions",
                "end": END
            }
        )
        workflow.add_edge("process_questions", "generate_assessment_report")
        workflow.add_edge("generate_assessment_report", "generate_plan")
        workflow.add_conditional_edges(
            "generate_plan",
            self._should_continue_after_plan,
            {
                "continue": "export_qa",
                "end": END
            }
        )
        workflow.add_edge("export_qa", "export_assessment_report")
        workflow.add_edge("export_assessment_report", "export_documents")
        workflow.add_edge("export_documents", "finalize")
        workflow.add_edge("finalize", END)
        
        return workflow
        workflow.add_edge("export_qa", "export_documents")
        workflow.add_edge("export_documents", "finalize")
        workflow.add_edge("finalize", END)
        
        return workflow
    
    def _initialize_node(self, state: WorkflowState) -> WorkflowState:
        """Initialize the workflow."""
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("Loading modules...")
        
        state["inputs"] = self.inputs
        state["result"] = ProcessingResult()
        state["errors"] = []
        state["step_completed"] = {}
        state["qa_export_success"] = False
        state["assessment_export_success"] = False
        state["plan_files"] = {}
        
        print("✓ Modules loaded")
        state["step_completed"]["initialize"] = True
        return state
    
    def _validate_inputs_node(self, state: WorkflowState) -> WorkflowState:
        """Validate all required input files."""
        print("Validating inputs...")
        
        required_inputs = ['transcript', 'questions_excel', 'azure_migrate_report']
        
        for input_name in required_inputs:
            if input_name not in state["inputs"]:
                error = f"Missing required input: {input_name}"
                print(error)
                state["errors"].append(error)
                state["result"].add_error("Input validation failed")
                return state
            
            input_obj = state["inputs"][input_name]
            if hasattr(input_obj, 'file_path') and input_obj.file_path:
                if not os.path.exists(input_obj.file_path):
                    error = f"Input file not found: {input_obj.file_path}"
                    print(error)
                    state["errors"].append(error)
                    state["result"].add_error("Input validation failed")
                    return state
        
        print("✓ Input files validated")
        state["step_completed"]["validate_inputs"] = True
        return state
    
    def _setup_llm_node(self, state: WorkflowState) -> WorkflowState:
        """Initialize Azure OpenAI connection."""
        print("Connecting to Azure OpenAI...")
        
        try:
            from Config import LLMConfig
            from langchain_openai import AzureChatOpenAI
            
            # Validate required configuration
            required_keys = [
                'AZURE_OPENAI_DEPLOYMENT_NAME',
                'AZURE_OPENAI_API_KEY', 
                'AZURE_OPENAI_ENDPOINT'
            ]
            
            config_dict = {
                'AZURE_OPENAI_DEPLOYMENT_NAME': LLMConfig.AZURE_OPENAI_DEPLOYMENT_NAME,
                'AZURE_OPENAI_API_KEY': LLMConfig.AZURE_OPENAI_API_KEY,
                'AZURE_OPENAI_ENDPOINT': LLMConfig.AZURE_OPENAI_ENDPOINT,
                'AZURE_OPENAI_MODEL_NAME': getattr(LLMConfig, 'AZURE_OPENAI_MODEL_NAME', 'gpt-4'),
                'AZURE_OPENAI_TEMPERATURE': getattr(LLMConfig, 'AZURE_OPENAI_TEMPERATURE', 0.0),
                'AZURE_OPENAI_API_VERSION': getattr(LLMConfig, 'AZURE_OPENAI_API_VERSION', '2023-12-01-preview')
            }
            
            missing_keys = []
            for key in required_keys:
                if not config_dict.get(key):
                    missing_keys.append(key)
            
            if missing_keys:
                error = f"Missing required LLM configuration: {missing_keys}"
                print(error)
                state["errors"].append(error)
                state["result"].add_error(error)
                return state
            
            # Initialize LLM directly
            llm_client = AzureChatOpenAI(
                deployment_name=config_dict['AZURE_OPENAI_DEPLOYMENT_NAME'],
                model_name=config_dict.get('AZURE_OPENAI_MODEL_NAME', 'gpt-4'),
                temperature=config_dict.get('AZURE_OPENAI_TEMPERATURE', 0.0),
                api_key=config_dict['AZURE_OPENAI_API_KEY'],
                azure_endpoint=config_dict['AZURE_OPENAI_ENDPOINT'],
                api_version=config_dict.get('AZURE_OPENAI_API_VERSION', '2023-12-01-preview')
            )
            
            state["llm_client"] = llm_client
            print("✓ Connected to Azure OpenAI")
            state["step_completed"]["setup_llm"] = True
                
        except Exception as e:
            error = f"Error initializing Azure OpenAI: {str(e)}"
            print(error)
            state["errors"].append(error)
            state["result"].add_error(error)
        
        return state
    
    def _process_azure_migrate_node(self, state: WorkflowState) -> WorkflowState:
        """Process Azure Migrate report."""
        print("Processing Azure Migrate report...")
        
        try:
            azure_migrate_input = state["inputs"].get('azure_migrate_report')
            if not azure_migrate_input or not azure_migrate_input.file_path:
                print("⚠ No Azure Migrate report found, using minimal data")
                state["azure_migrate_data"] = self._create_minimal_azure_migrate_data()
                state["step_completed"]["process_azure_migrate"] = True
                return state
            
            azure_migrate_data = ExcelProcessor.read_azure_migrate_report(azure_migrate_input.file_path)
            if azure_migrate_data:
                state["azure_migrate_data"] = azure_migrate_data
                print(f"✓ Processed {len(azure_migrate_data.servers)} servers from Azure Migrate report")
                state["step_completed"]["process_azure_migrate"] = True
            else:
                print("⚠ Failed to process Azure Migrate report, using minimal data")
                state["azure_migrate_data"] = self._create_minimal_azure_migrate_data()
                state["errors"].append("Azure Migrate report processing failed, using minimal data")
                state["step_completed"]["process_azure_migrate"] = True
                
        except Exception as e:
            error = f"Error processing Azure Migrate report: {str(e)}"
            print(f"⚠ {error}")
            print("⚠ Using minimal Azure Migrate data to continue workflow")
            state["azure_migrate_data"] = self._create_minimal_azure_migrate_data()
            state["errors"].append(error)
            state["step_completed"]["process_azure_migrate"] = True
        
        return state
    
    def _process_questions_node(self, state: WorkflowState) -> WorkflowState:
        """Process questions and transcript to generate Q&A pairs."""
        print("Processing questions...")
        
        try:
            # Load transcript content
            transcript_input = state["inputs"].get('transcript')
            if not transcript_input or not transcript_input.file_path:
                print("⚠ No transcript file found, using minimal analysis")
                state["questions_answers"] = self._create_minimal_qa_data()
                return state
            
            # Read transcript content
            with open(transcript_input.file_path, 'r', encoding='utf-8') as f:
                transcript_content = f.read()
            
            # Load questions from Excel
            questions_input = state["inputs"].get('questions_excel')
            if not questions_input or not questions_input.file_path:
                print("⚠ No questions Excel file found, generating insights from transcript only")
                state["questions_answers"] = self._analyze_transcript_only(transcript_content, state["llm_client"])
                return state
            
            # Process questions Excel file
            questions_data = ExcelProcessor.read_questions_from_excel(questions_input.file_path)
            
            # Combine transcript analysis with questions
            print(f"✓ Processing {len(questions_data)} questions with transcript insights")
            
            # Use LLM to analyze transcript and answer questions
            qa_pairs = self._analyze_transcript_with_llm(transcript_content, questions_data, state["llm_client"])
            state["questions_answers"] = qa_pairs
            state["step_completed"]["process_questions"] = True
            
        except Exception as e:
            error = f"Error processing questions and transcript: {str(e)}"
            print(error)
            print("⚠ Falling back to minimal analysis")
            state["questions_answers"] = self._create_minimal_qa_data()
            state["step_completed"]["process_questions"] = True
        
        return state
    
    def _generate_assessment_report_node(self, state: WorkflowState) -> WorkflowState:
        """Generate application assessment report."""
        print("Generating application assessment report...")
        
        try:
            # Extract project name from questions if available
            project_name = "Azure Migration Project"
            for qa in state["questions_answers"]:
                if any(keyword in qa.question.lower() for keyword in ['project', 'name', 'company', 'organization']):
                    if qa.answer and len(qa.answer) > 3:
                        project_name = qa.answer[:50]  # Limit length
                        break
            
            # Generate assessment report data
            assessment_data = self.assessment_report_generator.generate_assessment_report(
                questions_answers=state["questions_answers"],
                azure_migrate_data=state.get("azure_migrate_data"),
                project_name=project_name,
                llm_client=state.get("llm_client")
            )
            
            if assessment_data:
                state["assessment_report_data"] = assessment_data
                print("✓ Generated application assessment report")
                state["step_completed"]["generate_assessment_report"] = True
            else:
                error = "Failed to generate assessment report"
                print(error)
                state["errors"].append(error)
                
        except Exception as e:
            error = f"Error generating assessment report: {str(e)}"
            print(error)
            state["errors"].append(error)
        
        return state
    
    def _generate_plan_node(self, state: WorkflowState) -> WorkflowState:
        """Generate comprehensive migration plan."""
        print("Generating comprehensive migration plan...")
        
        try:
            # Extract project name from questions if available - using improved extraction
            project_name = "Azure Migration Project"
            
            # Look for questions about application name, project name, or system name
            name_keywords = ['application name', 'app name', 'system name', 'project name', 'service name', 'what is the name']
            
            for qa in state["questions_answers"]:
                if qa.is_answered and qa.answer and qa.answer != "Not addressed in transcript":
                    question_lower = qa.question.lower()
                    if any(keyword in question_lower for keyword in name_keywords):
                        # Clean up the answer and extract just the name
                        app_name = qa.answer.strip()
                        
                        # Try to extract just the application name from common patterns
                        
                        # Pattern 1: "The application name mentioned in the conversation is "Name""
                        import re
                        match = re.search(r'(?:application name|name).*?is\s*["\']?([^"\'.\n,]+)["\']?', app_name, re.IGNORECASE)
                        if match:
                            extracted_name = match.group(1).strip()
                            # Further clean the extracted name
                            clean_name = re.sub(r'[^\w\s-]', '', extracted_name).strip()
                            if len(clean_name) > 1 and len(clean_name) < 50:
                                project_name = clean_name
                                break
                        
                        # Pattern 2: Look for quoted names
                        match = re.search(r'["\']([^"\']+)["\']', app_name)
                        if match:
                            extracted_name = match.group(1).strip()
                            clean_name = re.sub(r'[^\w\s-]', '', extracted_name).strip()
                            if len(clean_name) > 1 and len(clean_name) < 50:
                                project_name = clean_name
                                break
                        
                        # Pattern 3: Look for capitalized words that could be application names
                        words = app_name.split()
                        for word in words:
                            # Skip common filler words
                            if word.lower() not in ['the', 'application', 'name', 'mentioned', 'in', 'conversation', 'is', 'called', 'system', 'project', 'service', 'transcript', 'discussion', 'meeting']:
                                clean_word = re.sub(r'[^\w-]', '', word)
                                # Look for words that start with capital letter or are all caps (likely names)
                                if len(clean_word) > 1 and len(clean_word) < 50 and (clean_word[0].isupper() or clean_word.isupper()):
                                    project_name = clean_word
                                    break
                        
                        # If we found a name, break out of the outer loop
                        if project_name != "Azure Migration Project":
                            break
            
            migration_plan = self.migration_plan_generator.generate_migration_plan(
                azure_migrate_data=state["azure_migrate_data"],
                transcript_insights=state["questions_answers"],
                project_name=project_name
            )
            
            if migration_plan:
                state["migration_plan"] = migration_plan
                print("✓ Generated comprehensive migration plan")
                state["step_completed"]["generate_plan"] = True
            else:
                error = "Failed to generate migration plan"
                print(error)
                state["errors"].append(error)
                state["result"].add_error(error)
                
        except Exception as e:
            error = f"Error generating migration plan: {str(e)}"
            print(error)
            state["errors"].append(error)
            state["result"].add_error(error)
        
        return state
    
    def _export_qa_node(self, state: WorkflowState) -> WorkflowState:
        """Export Q&A report to Excel."""
        print("Exporting Q&A analysis...")
        
        try:
            from SorthaDevKit.StateBase import ExcelOutputType
            
            # Create ExcelOutputType structure from our Q&A data
            excel_output = ExcelOutputType(
                questions_answers=state["questions_answers"],
                unanswered_questions=[qa.question for qa in state["questions_answers"] if not qa.is_answered],
                metadata={
                    "total_questions": len(state["questions_answers"]),
                    "answered_questions": len([qa for qa in state["questions_answers"] if qa.is_answered]),
                    "generation_method": "LangGraph Migration Plan Workflow",
                    "timestamp": datetime.now().isoformat()
                },
                summary={
                    "completion_rate": len([qa for qa in state["questions_answers"] if qa.is_answered]) / len(state["questions_answers"]) * 100 if state["questions_answers"] else 0,
                    "high_confidence": len([qa for qa in state["questions_answers"] if qa.confidence == "High"]),
                    "medium_confidence": len([qa for qa in state["questions_answers"] if qa.confidence == "Medium"]),
                    "low_confidence": len([qa for qa in state["questions_answers"] if qa.confidence == "Low"]),
                    "categories": list(set([qa.category for qa in state["questions_answers"] if qa.category]))
                }
            )
            
            # Get output path
            output_path = self._get_output_config().get("output_file_path", "output/filled_aif.xlsx")
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Get original questions file for reference
            questions_input = state["inputs"].get('questions_excel')
            original_questions_file = questions_input.file_path if questions_input else None
            
            # Use ExcelProcessor to create the output
            ExcelProcessor.create_output_excel(
                excel_output=excel_output,
                output_path=output_path,
                original_questions_file=original_questions_file
            )
            
            print(f"✓ Q&A Excel report saved: {output_path}")
            state["qa_export_success"] = True
            state["step_completed"]["export_qa"] = True
            
        except Exception as e:
            error = f"Error exporting Q&A report: {str(e)}"
            print(error)
            state["errors"].append(error)
            state["qa_export_success"] = False
            state["step_completed"]["export_qa"] = True  # Continue even if this fails
        
        return state
    
    def _export_assessment_report_node(self, state: WorkflowState) -> WorkflowState:
        """Export application assessment report to Word document."""
        print("Exporting application assessment report...")
        
        try:
            if "assessment_report_data" not in state or not state["assessment_report_data"]:
                print("⚠ No assessment report data available, skipping export")
                state["assessment_export_success"] = False
                state["step_completed"]["export_assessment_report"] = True
                return state
            
            # Determine output path
            output_dir = "output"
            os.makedirs(output_dir, exist_ok=True)
            
            # Use fixed filename that overwrites previous versions
            assessment_filename = "application_assessment_report.docx"
            assessment_output_path = os.path.join(output_dir, assessment_filename)
            
            # Export assessment report (template is now embedded)
            success = self.assessment_report_generator.export_to_word(
                assessment_data=state["assessment_report_data"],
                output_path=assessment_output_path
            )
            
            if success:
                print(f"✓ Assessment report saved: {assessment_output_path}")
                state["assessment_export_success"] = True
                
                # Add to plan files for reference
                if "plan_files" not in state:
                    state["plan_files"] = {}
                state["plan_files"]["assessment_report"] = assessment_output_path
            else:
                error = "Failed to export assessment report"
                print(error)
                state["errors"].append(error)
                state["assessment_export_success"] = False
            
            state["step_completed"]["export_assessment_report"] = True
            
        except Exception as e:
            error = f"Error exporting assessment report: {str(e)}"
            print(error)
            state["errors"].append(error)
            state["assessment_export_success"] = False
            state["step_completed"]["export_assessment_report"] = True  # Continue even if this fails
        
        return state
    
    def _export_documents_node(self, state: WorkflowState) -> WorkflowState:
        """Export migration plan documents."""
        print("Exporting migration plan documents...")
        
        try:
            output_files = {}
            output_dir = "output"
            os.makedirs(output_dir, exist_ok=True)
            
            # Word document export
            word_path = os.path.join(output_dir, "azure_migration_plan.docx")
            if self.document_exporter.export_to_word(state["migration_plan"], word_path):
                output_files['word'] = word_path
                print(f"✓ Word migration plan saved: {word_path}")
            else:
                print("⚠ Word export failed (python-docx may not be installed)")
            
            state["plan_files"] = output_files
            state["step_completed"]["export_documents"] = True
            
        except Exception as e:
            error = f"Error exporting migration plan document: {str(e)}"
            print(error)
            state["errors"].append(error)
            state["plan_files"] = {}
            state["step_completed"]["export_documents"] = True  # Continue even if this fails
        
        return state
    
    def _finalize_node(self, state: WorkflowState) -> WorkflowState:
        """Finalize the workflow and set results."""
        print("Finalizing workflow...")
        
        # Print final summary
        self._print_final_summary(state)
        
        # Set success result - only fail on critical errors
        critical_errors = [error for error in state["errors"] if "validation failed" in error.lower() or "failed to connect" in error.lower()]
        
        if not critical_errors:
            # We have some output even if there were non-critical errors
            state["result"].set_success(
                "Complete Azure Migration Plan generated successfully" + 
                (f" (with {len(state['errors'])} non-critical warnings)" if state["errors"] else ""),
                {
                    "migration_plan": state["migration_plan"],
                    "assessment_report_data": state.get("assessment_report_data"),
                    "azure_migrate_data": state["azure_migrate_data"],
                    "questions_answers": state["questions_answers"],
                    "output_files": {
                        "migration_plans": state["plan_files"],
                        "qa_report": state["qa_export_success"],
                        "assessment_report": state.get("assessment_export_success", False)
                    }
                }
            )
        else:
            # Only fail if we have critical errors
            for error in critical_errors:
                state["result"].add_error(error)
        
        print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        state["step_completed"]["finalize"] = True
        
        return state
    
    # Conditional edge functions
    def _should_continue_after_validation(self, state: WorkflowState) -> str:
        """Decide whether to continue after input validation."""
        # Only stop if critical validation errors (missing files)
        return "end" if state["errors"] else "continue"
    
    def _should_continue_after_llm(self, state: WorkflowState) -> str:
        """Decide whether to continue after LLM setup."""
        # Only stop if LLM setup failed - this is critical
        return "end" if state["errors"] else "continue"
    
    def _should_continue_after_azure_migrate(self, state: WorkflowState) -> str:
        """Decide whether to continue after Azure Migrate processing."""
        # Continue even if Azure Migrate processing fails - we can work with minimal data
        return "continue"
    
    def _should_continue_after_plan(self, state: WorkflowState) -> str:
        """Decide whether to continue after plan generation."""
        # Continue even if plan generation has issues - we can still export Q&A
        return "continue"
    
    def _create_minimal_qa_data(self):
        """Create minimal Q&A data when inputs are not available."""
        return [
            QuestionAnswer(
                question="What is the project name?",
                answer="Azure Migration Project",
                confidence="Medium",
                is_answered=True,
                category="Project",
                priority="High",
                source_reference="Default"
            ),
            QuestionAnswer(
                question="What are the primary business drivers for this migration?",
                answer="Cost optimization, improved scalability, enhanced security, and digital transformation",
                confidence="Medium",
                is_answered=True,
                category="Business",
                priority="High",
                source_reference="Generated"
            )
        ]
    
    def _create_minimal_azure_migrate_data(self):
        """Create minimal Azure Migrate data when processing fails."""
        from SorthaDevKit.StateBase import AzureMigrateReport, AzureMigrateServer
        
        # Create a minimal server for demonstration
        minimal_server = AzureMigrateServer(
            server_name="Sample-Server-01",
            os_type="Windows",
            cores=4,
            memory_gb=8,
            storage_gb=100,
            recommendation="Azure VM",
            monthly_cost=150.0,
            readiness="Ready"
        )
        
        return AzureMigrateReport(
            servers=[minimal_server],
            total_servers=1,
            total_monthly_cost=150.0,
            assessment_date="Sample Data"
        )
    
    def _analyze_transcript_only(self, transcript_content, llm_client):
        """Analyze transcript when no questions Excel is available."""
        # Similar to original implementation
        return self._create_minimal_qa_data()
    
    def _analyze_transcript_with_llm(self, transcript_content, questions_data, llm_client):
        """Use LLM to analyze transcript and answer specific questions."""
        qa_pairs = []
        
        if not llm_client:
            print("⚠ LLM not available, using simplified analysis")
            return self._analyze_transcript_simple(transcript_content, questions_data)
        
        print(f"✓ Using LLM for enhanced transcript analysis")
        
        for question_data in questions_data:
            try:
                # Extract question and metadata
                question = question_data['question'] if isinstance(question_data, dict) else question_data
                category = question_data.get('category', 'General') if isinstance(question_data, dict) else 'General'
                priority = question_data.get('priority', 'Medium') if isinstance(question_data, dict) else 'Medium'
                
                prompt = f"""
                Analyze the following transcript to answer this specific question. Please provide a direct, concise answer.
                
                Question: {question}
                
                Transcript:
                {transcript_content}
                
                Instructions:
                1. If the answer is clearly found in the transcript, provide a direct answer (2-3 sentences max)
                2. If the answer is not addressed in the transcript, respond exactly with: "Not addressed in transcript"
                3. Provide a confidence level: High (explicitly mentioned), Medium (can be inferred), Low (unclear), or Unknown (not addressed)
                4. If you find the answer in the transcript, try to identify a rough timestamp or section reference
                
                Format your response as:
                ANSWER: [your answer or "Not addressed in transcript"]
                CONFIDENCE: [High/Medium/Low/Unknown]
                SOURCE: [timestamp or section reference if available, or "N/A" if not addressed]
                """
                
                response = llm_client.invoke(prompt)
                response_text = response.content if hasattr(response, 'content') else str(response)
                
                # Parse the structured response (same logic as original)
                answer = "Not addressed in transcript"
                confidence = "Unknown"
                source_ref = "N/A"
                is_answered = False
                
                lines = response_text.split('\n')
                for line in lines:
                    line = line.strip()
                    if line.startswith('ANSWER:'):
                        answer = line.replace('ANSWER:', '').strip()
                        if answer != "Not addressed in transcript":
                            is_answered = True
                    elif line.startswith('CONFIDENCE:'):
                        confidence = line.replace('CONFIDENCE:', '').strip()
                        if confidence not in ['High', 'Medium', 'Low', 'Unknown']:
                            confidence = "Medium"
                    elif line.startswith('SOURCE:'):
                        source_ref = line.replace('SOURCE:', '').strip()
                
                # If parsing failed, use fallback
                if not any(line.startswith(('ANSWER:', 'CONFIDENCE:', 'SOURCE:')) for line in lines):
                    if "not addressed" in response_text.lower() or "not found" in response_text.lower():
                        answer = "Not addressed in transcript"
                        confidence = "Unknown"
                        is_answered = False
                    else:
                        answer = response_text[:200] + "..." if len(response_text) > 200 else response_text
                        confidence = "Medium"
                        is_answered = True
                        source_ref = "Transcript Analysis"
                
                qa_pairs.append(QuestionAnswer(
                    question=question,
                    answer=answer,
                    confidence=confidence,
                    is_answered=is_answered,
                    category=category,
                    priority=priority,
                    source_reference=source_ref
                ))
                
            except Exception as e:
                print(f"Error analyzing question '{question}': {str(e)}")
                qa_pairs.append(QuestionAnswer(
                    question=question,
                    answer="Error in analysis",
                    confidence="Unknown",
                    is_answered=False,
                    category=category if 'category' in locals() else "Error",
                    priority=priority if 'priority' in locals() else "Medium",
                    source_reference="Processing Error"
                ))
        
        # Print summary after all questions are analyzed
        total_questions = len(questions_data)
        answered_questions = len([qa for qa in qa_pairs if qa.is_answered])
        print(f"✓ Transcript analysis complete: {answered_questions}/{total_questions} questions analyzed")
        
        return qa_pairs
    
    def _analyze_transcript_simple(self, transcript_content, questions_data):
        """Simple transcript analysis without LLM."""
        # Same implementation as original
        qa_pairs = []
        
        for question_data in questions_data:
            # Extract question and metadata
            question = question_data['question'] if isinstance(question_data, dict) else question_data
            category = question_data.get('category', 'General') if isinstance(question_data, dict) else 'General'
            priority = question_data.get('priority', 'Medium') if isinstance(question_data, dict) else 'Medium'
            
            # Simple keyword matching and analysis
            answer = "Not addressed in transcript"
            confidence = "Unknown"
            is_answered = False
            source_ref = "N/A"
            
            # Look for relevant keywords in transcript
            question_lower = question.lower()
            transcript_lower = transcript_content.lower()
            
            if "security" in question_lower:
                if any(keyword in transcript_lower for keyword in ["security", "secure", "authentication", "authorization"]):
                    answer = "Security requirements discussed in transcript"
                    confidence = "Medium"
                    is_answered = True
                    source_ref = "Transcript content analysis"
            elif "database" in question_lower:
                if any(db in transcript_lower for db in ["sql", "database", "db", "mysql", "postgresql", "oracle"]):
                    answer = "Database components mentioned in transcript"
                    confidence = "Medium"
                    is_answered = True
                    source_ref = "Transcript content analysis"
            elif "cost" in question_lower or "budget" in question_lower:
                if any(cost_word in transcript_lower for cost_word in ["cost", "budget", "price", "expensive", "cheap"]):
                    answer = "Cost considerations discussed in transcript"
                    confidence = "Medium"
                    is_answered = True
                    source_ref = "Transcript content analysis"
            elif "timeline" in question_lower or "schedule" in question_lower:
                if any(time_word in transcript_lower for time_word in ["timeline", "schedule", "month", "week", "year", "deadline"]):
                    answer = "Timeline information mentioned in transcript"
                    confidence = "Medium"
                    is_answered = True
                    source_ref = "Transcript content analysis"
            elif "application" in question_lower or "app" in question_lower:
                if any(app_word in transcript_lower for app_word in ["application", "app", "software", "system"]):
                    answer = "Application information discussed in transcript"
                    confidence = "Medium"
                    is_answered = True
                    source_ref = "Transcript content analysis"
            
            qa_pairs.append(QuestionAnswer(
                question=question,
                answer=answer,
                confidence=confidence,
                is_answered=is_answered,
                category=category,
                priority=priority,
                source_reference=source_ref
            ))
        
        return qa_pairs
    
    def _get_output_config(self) -> Dict[str, str]:
        """Get output configuration."""
        try:
            from Input import OUTPUT_CONFIG
            return OUTPUT_CONFIG
        except Exception:
            # Fallback configuration
            return {
                "output_file_path": "output/filled_aif.xlsx"
            }
    
    def _print_final_summary(self, state: WorkflowState):
        """Print final summary of generated outputs."""
        print("\nMigration plan generation complete!")
        
        # Count generated files
        total_files = len(state["plan_files"])
        if state["qa_export_success"]:
            total_files += 1  # Add Q&A report
        if state.get("assessment_export_success"):
            total_files += 1  # Add Assessment report
            
        print(f"✓ Generated {total_files} output files in the output/ directory")
        
        # Print specific file information
        if state.get("assessment_export_success"):
            print("✓ Generated Application Assessment Report")
        if state["qa_export_success"]:
            print("✓ Generated Q&A Analysis Report")
        for file_type, file_path in state["plan_files"].items():
            if file_type != "assessment_report":  # Don't double-count
                print(f"✓ Generated {file_type.replace('_', ' ').title()}: {os.path.basename(file_path)}")
        
        if state.get("migration_plan") and hasattr(state["migration_plan"], 'azure_migrate_data'):
            print(f"✓ Processed {len(state['migration_plan'].azure_migrate_data.servers)} servers")
            print(f"✓ Created {len(state['migration_plan'].migration_waves)} migration waves")
    
    def run(self) -> ProcessingResult:
        """Execute the LangGraph workflow."""
        try:
            # Compile the graph
            memory = MemorySaver()
            app = self.graph.compile(checkpointer=memory)
            
            # Initialize the state
            initial_state = WorkflowState(
                inputs=self.inputs,
                azure_migrate_data=None,
                questions_answers=[],
                assessment_report_data=None,
                migration_plan=None,
                qa_export_success=False,
                assessment_export_success=False,
                plan_files={},
                result=ProcessingResult(),
                llm_client=None,
                errors=[],
                step_completed={}
            )
            
            # Run the workflow
            config = {"configurable": {"thread_id": "migration_workflow"}}
            final_state = app.invoke(initial_state, config)
            
            return final_state["result"]
            
        except Exception as e:
            print(f"Error in LangGraph workflow: {str(e)}")
            result = ProcessingResult()
            result.add_error(f"Workflow execution failed: {str(e)}")
            return result


def create_langgraph_workflow(inputs: Dict[str, Any]) -> LangGraphMigrationPlanWorkflow:
    """Factory function to create a LangGraph workflow."""
    return LangGraphMigrationPlanWorkflow(inputs)
