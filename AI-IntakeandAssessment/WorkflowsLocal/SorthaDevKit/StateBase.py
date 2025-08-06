from pydantic import BaseModel, Field
from typing import Union, List, Dict, Any, Optional
from enum import StrEnum
from datetime import datetime
from dataclasses import dataclass, field

class FileTypes(StrEnum):
    TEXT = 'text'
    EXCEL = 'excel'
    UNDEFINED = 'undefined'

class FileInputType(BaseModel):
    type: FileTypes = Field(default=FileTypes.UNDEFINED, description="Type of input, e.g. 'text', 'file', etc.")
    file_path: str = Field(default='', description="Path to the file input")
    content: str = Field(default='', description="Content of the input, e.g. text or file content")

class UserInputType(BaseModel):
    content: str = Field(default='', description="Content of the input, e.g. text or file content")

class StateBase(BaseModel):
    inputs: dict[str, Union[FileInputType, UserInputType]] = Field(default={}, description="Dictionary of inputs")
    output: str = Field(default='', description="Output of the workflow")

class QuestionAnswer(BaseModel):
    question: str
    answer: str = ""
    confidence: str = "Medium"
    source_reference: str = ""
    is_answered: bool = False
    category: str = ""
    priority: str = "Medium"
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class ExcelOutputType(BaseModel):
    questions_answers: List[QuestionAnswer] = Field(default_factory=list)
    unanswered_questions: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    summary: Dict[str, Any] = Field(default_factory=dict)

class AzureMigrateServer(BaseModel):
    server_name: str = ""
    server_type: str = ""
    operating_system: str = ""
    cpu_cores: int = 0
    memory_gb: float = 0.0
    disk_size_gb: float = 0.0
    network_adapters: int = 0
    applications: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    recommendation: str = ""
    azure_vm_size: str = ""
    storage_type: str = ""
    estimated_cost: float = 0.0
    readiness: str = ""
    confidence: str = ""
    warnings: List[str] = Field(default_factory=list)
    # Additional Azure Migrate specific fields
    azure_readiness_reason: str = ""
    monthly_compute_cost: float = 0.0
    monthly_storage_cost: float = 0.0
    boot_type: str = ""
    discovered_applications: List[str] = Field(default_factory=list)

class AzureMigrateReport(BaseModel):
    servers: List[AzureMigrateServer] = Field(default_factory=list)
    summary: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    report_date: str = Field(default_factory=lambda: datetime.now().isoformat())

class ArchitectureComponent(BaseModel):
    component_id: str
    component_type: str  # VM, Database, LoadBalancer, Network, etc.
    name: str
    azure_service: str  # Specific Azure service (e.g., Azure VM, Azure SQL, etc.)
    tier: str  # Presentation, Application, Data, Network
    position: Dict[str, float] = Field(default_factory=dict)  # x, y coordinates
    properties: Dict[str, Any] = Field(default_factory=dict)
    connections: List[str] = Field(default_factory=list)  # Connected component IDs
    source_server: Optional[str] = None  # Original server from Azure Migrate
    migration_type: str = "lift-and-shift"  # lift-and-shift, modernize, rearchitect

class ArchitectureDiagram(BaseModel):
    diagram_id: str = Field(default_factory=lambda: f"arch_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    title: str = "Azure Target Architecture"
    components: List[ArchitectureComponent] = Field(default_factory=list)
    networks: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_date: str = Field(default_factory=lambda: datetime.now().isoformat())

class WorkflowState(BaseModel):
    current_step: str = ""
    progress: float = 0.0
    status: str = "initialized"
    errors: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def add_error(self, error: str):
        self.errors.append(error)
        self.status = "error"
    
    def set_progress(self, progress: float, step: str = ""):
        self.progress = max(0.0, min(100.0, progress))
        if step:
            self.current_step = step
        
        if self.progress >= 100.0:
            self.status = "completed"
        elif self.progress > 0:
            self.status = "running"

class ProcessingResult(BaseModel):
    success: bool = False
    message: str = ""
    data: Any = None
    errors: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def add_error(self, error: str):
        self.errors.append(error)
        self.success = False
    
    def set_success(self, message: str = "", data: Any = None):
        self.success = True
        if message:
            self.message = message
        if data is not None:
            self.data = data

@dataclass
class MigrationWave:
    wave_number: int
    name: str
    description: str
    servers: List[AzureMigrateServer]
    duration_weeks: int
    dependencies: List[str]
    risk_level: str  # Low, Medium, High, Critical
    estimated_cost: float
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    prerequisites: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)

@dataclass
class MigrationRisk:
    risk_id: str
    description: str
    impact: str  # Low, Medium, High, Critical
    probability: str  # Low, Medium, High
    mitigation: str
    owner: str
    category: str  # Technical, Business, Security, Operational

@dataclass
class CostEstimate:
    category: str  # Compute, Storage, Network, Management, etc.
    current_monthly_cost: float
    azure_monthly_cost: float
    one_time_migration_cost: float
    annual_savings: float
    roi_months: int
    details: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MigrationTimeline:
    total_duration_months: int
    waves: List[MigrationWave]
    key_milestones: List[Dict[str, str]]
    critical_path: List[str]
    resource_requirements: Dict[str, Any]

@dataclass
class AzureMigrationPlan:
    project_name: str
    executive_summary: str
    business_case: str
    
    # Current State Assessment
    current_infrastructure: Dict[str, Any]
    azure_migrate_data: AzureMigrateReport
    
    # Target Architecture
    target_services: List[Dict[str, Any]]
    
    # Migration Strategy
    migration_approach: str
    migration_timeline: MigrationTimeline
    migration_waves: List[MigrationWave]
    
    # Risk Assessment
    risks: List[MigrationRisk]
    assumptions: List[str]
    constraints: List[str]
    
    # Cost Analysis
    cost_estimates: List[CostEstimate]
    total_investment: float
    expected_savings: float
    
    # Implementation Plan
    resource_plan: Dict[str, Any]
    training_plan: Dict[str, Any]
    communication_plan: Dict[str, Any]
    
    # Governance & Compliance
    security_requirements: List[str]
    compliance_requirements: List[str]
    governance_model: Dict[str, Any]
    
    # Success Metrics
    kpis: List[Dict[str, Any]]
    success_criteria: List[str]
    
    # Appendices
    technical_specifications: Dict[str, Any]
    vendor_requirements: List[str]
    
    # Metadata
    document_version: str = "1.0"
    created_date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    created_by: str = "Suchitha Malisetty"
    last_updated: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))