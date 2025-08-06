from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, TypeVar, Callable
from datetime import datetime
import logging
import os
import json
import re
from .StateBase import WorkflowState, ProcessingResult, QuestionAnswer, ExcelOutputType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

T = TypeVar('T', bound=WorkflowState)

class StateGraph:
    def __init__(self):
        self.nodes = {}
        self.edges = []
    
    def add_node(self, node_name: str, node_function: Callable):
        self.nodes[node_name] = node_function
    
    def add_edge(self, from_node: str, to_node: str):
        self.edges.append((from_node, to_node))
    
    def __getitem__(self, key):
        if key == "nodes":
            return self.nodes
        elif key == "edges":
            return self.edges
        else:
            raise KeyError(f"Unknown key: {key}")

class WorkFlowBase(ABC):
    def __init__(self, name: str = "BaseWorkflow"):
        self.name = name
        self.state: Optional[WorkflowState] = None
        self.steps: List[str] = []
        self.current_step_index: int = 0
        self.logger = logging.getLogger(f"{__name__}.{name}")
        self._state_graph: Optional[StateGraph] = None
        self._start_node = "START"
        self._end_node = "END"
    
    def createStateGraph(self, state_type):
        """Create state graph for the workflow."""
        self._state_graph = StateGraph()
        return self._state_graph
    
    def getStateGraph(self) -> StateGraph:
        """Get the state graph."""
        if not self._state_graph:
            self.createStateGraph(None)
        return self._state_graph
    
    def getStartNodePointer(self) -> str:
        """Get start node pointer."""
        return self._start_node
    
    def getEndNodePointer(self) -> str:
        """Get end node pointer."""
        return self._end_node
    
    def buildGraph(self):
        """Build the workflow graph. Should be implemented by subclasses."""
        pass
        
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the workflow with configuration."""
        pass
    
    @abstractmethod
    def execute(self, input_data: Any) -> ProcessingResult:
        """Execute the main workflow logic."""
        pass
    
    @abstractmethod
    def cleanup(self) -> bool:
        """Clean up resources after workflow execution."""
        pass
    
    def validate_input(self, input_data: Any) -> bool:
        """Validate input data before processing."""
        if input_data is None:
            self.logger.error("Input data cannot be None")
            return False
        return True
    
    def set_state(self, state: WorkflowState):
        """Set the current workflow state."""
        self.state = state
        print(f"State set: {state.status}")
    
    def update_progress(self, progress: float, step: str = ""):
        """Update workflow progress."""
        if self.state:
            self.state.set_progress(progress, step)
            print(f"Progress: {progress}% - {step}")
    
    def add_error(self, error: str):
        """Add an error to the workflow state."""
        if self.state:
            self.state.add_error(error)
        self.logger.error(error)
    
    def run(self, input_data: Any, config: Optional[Dict[str, Any]] = None) -> ProcessingResult:
        """Run the complete workflow."""
        result = ProcessingResult()
        
        try:
            # Initialize
            print(f"Starting workflow: {self.name}")
            
            if config and not self.initialize(config):
                result.add_error("Failed to initialize workflow")
                return result
            
            # Validate input
            if not self.validate_input(input_data):
                result.add_error("Input validation failed")
                return result
            
            # Execute
            print("Executing workflow")
            result = self.execute(input_data)
            
            # Cleanup
            if not self.cleanup():
                self.logger.warning("Cleanup completed with warnings")
            
            if result.success:
                print(f"Workflow completed successfully: {self.name}")
            else:
                self.logger.error(f"Workflow failed: {self.name}")
                
        except Exception as e:
            error_msg = f"Workflow execution failed: {str(e)}"
            self.logger.error(error_msg)
            result.add_error(error_msg)
        
        return result
    
    def get_status(self) -> Dict[str, Any]:
        """Get current workflow status."""
        status = {
            "name": self.name,
            "current_step_index": self.current_step_index,
            "total_steps": len(self.steps),
            "timestamp": datetime.now().isoformat()
        }
        
        if self.state:
            status.update({
                "current_step": self.state.current_step,
                "progress": self.state.progress,
                "status": self.state.status,
                "errors": self.state.errors
            })
        
        return status

class QuestionAnsweringWorkFlowBase(WorkFlowBase):
    """Base class for AIF filling workflows with common functionality."""
    
    def __init__(self, name: str = "QAWorkflow"):
        """Initialize the QA workflow."""
        super().__init__(name)
        self.llm_client = None
        self.transcript_content = ""
        self.questions = []
        self._processing_stats = {}
        
    def initialize_llm(self, config: Dict[str, Any]) -> bool:
        """Initialize LLM with configuration validation and error handling."""
        try:
            # Import here to avoid circular dependencies
            from langchain_openai import AzureChatOpenAI
            
            # Validate required configuration
            required_keys = [
                'AZURE_OPENAI_DEPLOYMENT_NAME',
                'AZURE_OPENAI_API_KEY', 
                'AZURE_OPENAI_ENDPOINT'
            ]
            
            missing_keys = []
            for key in required_keys:
                if not config.get(key):
                    missing_keys.append(key)
            
            if missing_keys:
                raise ValueError(f"Missing required LLM configuration: {missing_keys}")
            
            # Initialize LLM
            self.llm_client = AzureChatOpenAI(
                deployment_name=config['AZURE_OPENAI_DEPLOYMENT_NAME'],
                model_name=config.get('AZURE_OPENAI_MODEL_NAME', 'gpt-4'),
                temperature=config.get('AZURE_OPENAI_TEMPERATURE', 0.0),
                api_key=config['AZURE_OPENAI_API_KEY'],
                azure_endpoint=config['AZURE_OPENAI_ENDPOINT'],
                api_version=config.get('AZURE_OPENAI_API_VERSION', '2023-12-01-preview')
            )
            
            print(f"LLM initialized: {config.get('AZURE_OPENAI_MODEL_NAME', 'gpt-4')}")
            return True
            
        except Exception as e:
            self.add_error(f"Failed to initialize LLM: {str(e)}")
            return False
    
    def validate_file_inputs(self, transcript_path: str, questions_path: str, output_path: str) -> bool:
        """Validate input and output file paths."""
        try:
            # Check transcript file exists
            if not os.path.exists(transcript_path):
                self.add_error(f"Transcript file not found: {transcript_path}")
                return False
            
            # Check questions file exists
            if not os.path.exists(questions_path):
                self.add_error(f"Questions file not found: {questions_path}")
                return False
            
            # Ensure output directory exists
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                try:
                    os.makedirs(output_dir)
                    print(f"Created output directory: {output_dir}")
                except Exception as e:
                    self.add_error(f"Failed to create output directory: {str(e)}")
                    return False
            
            return True
            
        except Exception as e:
            self.add_error(f"File validation failed: {str(e)}")
            return False

    def load_transcript_from_file(self, file_path: str) -> bool:
        """Load transcript from file with error handling."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.transcript_content = f.read()
            
            if not self.transcript_content.strip():
                self.add_error("Transcript file is empty")
                return False
                
            print(f"Transcript loaded: {len(self.transcript_content)} characters")
            return True
            
        except Exception as e:
            self.add_error(f"Failed to load transcript: {str(e)}")
            return False
    
    def load_questions_from_excel(self, file_path: str, question_column: str = 'Question', sheet_name: str = None) -> bool:
        """Load questions from Excel file using ExcelProcessor."""
        try:
            from .ExcelUtils import ExcelProcessor
            
            self.questions = ExcelProcessor.read_questions_from_excel(
                file_path,
                question_column=question_column,
                sheet_name=sheet_name
            )
            
            if not self.questions:
                self.add_error("No questions found in Excel file")
                return False
                
            # Suppressed: print(f"Questions loaded: {len(self.questions)}")
            return True
            
        except Exception as e:
            self.add_error(f"Failed to load questions: {str(e)}")
            return False
    
    def create_question_prompt(self, question: str, transcript: str) -> str:
        """Create a standardized prompt for question answering."""
        return f"""
You are an expert transcript analyzer. Your task is to answer a specific question based on the provided conversation transcript.

QUESTION TO ANSWER:
{question}

CONVERSATION TRANSCRIPT:
{transcript}

INSTRUCTIONS:
1. Carefully read the transcript and look for information that directly or indirectly answers the question.
2. Provide your response in the following JSON format:

{{
    "answer": "Your detailed answer here, or 'Not addressed in transcript' if no relevant information found",
    "confidence": "High|Medium|Low|Unknown",
    "source_reference": "Brief reference to the part of transcript where answer was found",
    "is_answered": true|false
}}

GUIDELINES:
- Use "High" confidence when the answer is explicitly stated in the transcript
- Use "Medium" confidence when the answer can be reasonably inferred
- Use "Low" confidence when only partial or unclear information is available
- Use "Unknown" confidence when no relevant information is found
- Set "is_answered" to true only if you found relevant information in the transcript
- For "source_reference", include speaker names and brief context when possible
- If multiple parts of the transcript are relevant, reference the most important one

Provide only the JSON response, no additional text.
"""
    
    def parse_llm_response(self, question: str, llm_response: str) -> QuestionAnswer:
        """Parse LLM response into QuestionAnswer object with robust error handling."""
        try:
            json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
            if json_match:
                response_data = json.loads(json_match.group())
                
                return QuestionAnswer(
                    question=question,
                    answer=response_data.get('answer', 'No answer provided'),
                    confidence=response_data.get('confidence', 'Unknown'),
                    source_reference=response_data.get('source_reference', ''),
                    is_answered=response_data.get('is_answered', False)
                )
            else:
                return QuestionAnswer(
                    question=question,
                    answer=llm_response.strip(),
                    confidence='Unknown',
                    source_reference='',
                    is_answered='not addressed' not in llm_response.lower()
                )
                
        except Exception as e:
            self.logger.error(f"Failed to parse LLM response: {str(e)}")
            return QuestionAnswer(
                question=question,
                answer=f"Error parsing response: {str(e)}",
                confidence='Unknown',
                source_reference='',
                is_answered=False
            )
    
    def process_single_question(self, question: str, show_progress: bool = True, question_index: int = 0, total_questions: int = 0) -> QuestionAnswer:
        """Process a single question with the LLM."""
        try:
            if not self.llm_client:
                raise ValueError("LLM not initialized")
            
            if not self.transcript_content:
                raise ValueError("Transcript content not loaded")
            
            # Show progress if requested
            # Suppressed per-question progress output

            # Create prompt and get LLM response
            prompt = self.create_question_prompt(question, self.transcript_content)
            response = self.llm_client.invoke(prompt).content
            
            # Parse response
            qa = self.parse_llm_response(question, response)
            
            # Update processing stats
            if hasattr(self, '_processing_stats'):
                self._processing_stats['questions_processed'] = self._processing_stats.get('questions_processed', 0) + 1
                if qa.is_answered:
                    self._processing_stats['questions_answered'] = self._processing_stats.get('questions_answered', 0) + 1
            
            return qa
            
        except Exception as e:
            error_msg = f"Failed to process question: {str(e)}"
            self.logger.error(error_msg)
            return QuestionAnswer(
                question=question,
                answer=f"Processing error: {str(e)}",
                confidence='Unknown',
                source_reference='',
                is_answered=False
            )
    
    def process_all_questions(self, questions: List[str] = None) -> List[QuestionAnswer]:
        """Process all questions and return results."""
        if questions is None:
            questions = self.questions
        
        if not questions:
            self.add_error("No questions to process")
            return []
        
        try:
            # Suppressed batch processing output
            questions_answers = []
            
            for i, question in enumerate(questions):
                qa = self.process_single_question(question, True, i, len(questions))
                questions_answers.append(qa)
            
            # Suppressed batch completion output
            return questions_answers
            
        except Exception as e:
            self.add_error(f"Failed to process questions: {str(e)}")
            return []
    
    def create_excel_output(self, questions_answers: List[QuestionAnswer], output_path: str, original_file_path: str = None) -> bool:
        """Create Excel output file with results."""
        try:
            from .ExcelUtils import ExcelProcessor
            
            # Create ExcelOutputType object
            unanswered_questions = [qa.question for qa in questions_answers if not qa.is_answered]
            answered_count = len([qa for qa in questions_answers if qa.is_answered])
            
            excel_output = ExcelOutputType(
                questions_answers=questions_answers,
                unanswered_questions=unanswered_questions,
                summary={
                    "total_questions": len(questions_answers),
                    "answered_questions": answered_count,
                    "processing_status": "completed",
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            # Create Excel file
            ExcelProcessor.create_output_excel(excel_output, output_path, original_file_path)
            
            print(f"Excel output created: {output_path}")
            return True
            
        except Exception as e:
            self.add_error(f"Failed to create Excel output: {str(e)}")
            return False
    
    def get_processing_summary(self, questions_answers: List[QuestionAnswer] = None) -> Dict[str, Any]:
        """Get a summary of processing results."""
        if questions_answers is None:
            return self._processing_stats
        
        total = len(questions_answers)
        answered = len([qa for qa in questions_answers if qa.is_answered])
        
        confidence_dist = {}
        for qa in questions_answers:
            conf = qa.confidence
            confidence_dist[conf] = confidence_dist.get(conf, 0) + 1
        
        return {
            "total_questions": total,
            "answered_questions": answered,
            "unanswered_questions": total - answered,
            "answer_rate_percent": (answered / total * 100) if total > 0 else 0,
            "confidence_distribution": confidence_dist,
            "processing_time": getattr(self._processing_stats, 'processing_time', 'Unknown'),
            "timestamp": datetime.now().isoformat()
        }