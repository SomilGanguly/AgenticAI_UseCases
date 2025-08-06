import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import asdict
import math
import statistics
import openai
import os
from dotenv import load_dotenv
from .StateBase import (
    AzureMigrationPlan, AzureMigrateReport, ArchitectureDiagram, 
    MigrationWave, MigrationRisk, CostEstimate, MigrationTimeline,
    AzureMigrateServer, QuestionAnswer
)

# Load environment variables from .env file
load_dotenv()

class AzureMigrationPlanGenerator:
    """Generator for comprehensive Azure Migration Plan documents using AI-driven content generation."""
    
    def __init__(self, ai_client=None):
        """
        Initialize the migration plan generator with configuration from .env file.
        
        Args:
            ai_client: Optional AI client for content generation. If None, will attempt to initialize from .env.
        """
        self.migration_strategies = {
            "lift-and-shift": "Rehost applications in Azure with minimal changes",
            "modernize": "Refactor applications to leverage Azure PaaS services",
            "rearchitect": "Rebuild applications with cloud-native architecture",
            "replace": "Replace with Azure SaaS solutions",
            "retire": "Decommission applications no longer needed"
        }
        
        self.risk_categories = {
            "technical": "Technical risks related to compatibility and performance",
            "business": "Business risks related to operations and continuity",
            "security": "Security and compliance related risks",
            "operational": "Operational risks related to deployment and management"
        }
        
        # Load configuration from .env file
        self.config = self._load_config()
        
        # Initialize AI client for content generation
        self.ai_client = ai_client
        if self.ai_client is None:
            self.ai_client = self._initialize_ai_client()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration settings from .env file."""
        return {
            # AI Settings
            "ai_temperature": float(os.getenv("AI_TEMPERATURE", os.getenv("AZURE_OPENAI_TEMPERATURE", "0.7"))),
            "ai_max_tokens": int(os.getenv("AI_MAX_TOKENS", "2000")),
            "ai_timeout_seconds": int(os.getenv("AI_TIMEOUT_SECONDS", "60")),
            "ai_model": os.getenv("OPENAI_MODEL", os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")),
            "ai_api_version": os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
            
            # Content Generation Preferences
            "content_style": os.getenv("CONTENT_STYLE", "professional"),
            "detail_level": os.getenv("DETAIL_LEVEL", "comprehensive"),
            "include_technical_details": os.getenv("INCLUDE_TECHNICAL_DETAILS", "true").lower() == "true",
            "include_cost_analysis": os.getenv("INCLUDE_COST_ANALYSIS", "true").lower() == "true",
            "include_risk_assessment": os.getenv("INCLUDE_RISK_ASSESSMENT", "true").lower() == "true",
            
            # Migration Plan Customization
            "default_project_name": os.getenv("DEFAULT_PROJECT_NAME", "Azure Migration Project"),
            "organization_name": os.getenv("ORGANIZATION_NAME", "Your Organization"),
            "include_vendor_recommendations": os.getenv("INCLUDE_VENDOR_RECOMMENDATIONS", "true").lower() == "true",
            "generate_timeline_charts": os.getenv("GENERATE_TIMELINE_CHARTS", "true").lower() == "true",
        }
    
    def _initialize_ai_client(self):
        """Initialize AI client based on .env configuration."""
        try:
            # Try Azure OpenAI first
            azure_api_key = os.getenv('AZURE_OPENAI_API_KEY')
            azure_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
            azure_api_version = os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-01')
            
            if azure_api_key and azure_endpoint:
                return openai.AzureOpenAI(
                    api_key=azure_api_key,
                    api_version=azure_api_version,
                    azure_endpoint=azure_endpoint
                )
            
            # Fall back to standard OpenAI
            openai_api_key = os.getenv('OPENAI_API_KEY')
            if openai_api_key:
                return openai.OpenAI(api_key=openai_api_key)
                
        except Exception as e:
            print(f"Warning: Could not initialize AI client: {e}")
            
        return None
    
    def configure_ai_client(self, client=None, api_key=None, endpoint=None, model_name=None):
        """
        Configure AI client for content generation.
        
        Args:
            client: Pre-configured AI client
            api_key: API key for AI service
            endpoint: Endpoint URL (for Azure OpenAI)
            model_name: Model name to use for generation
        """
        if client:
            self.ai_client = client
        elif api_key:
            try:
                if endpoint:
                    # Azure OpenAI
                    self.ai_client = openai.AzureOpenAI(
                        api_key=api_key,
                        api_version="2024-02-01",
                        azure_endpoint=endpoint
                    )
                else:
                    # Standard OpenAI
                    self.ai_client = openai.OpenAI(api_key=api_key)
                    
                if model_name:
                    self.model_name = model_name
                    
            except Exception as e:
                print(f"Error configuring AI client: {e}")
                self.ai_client = None
    
    def _generate_ai_content(self, prompt: str, context_data: Dict[str, Any] = None) -> str:
        """
        Generate content using AI based on prompt and context data with configuration from .env.
        
        Args:
            prompt: The prompt for content generation
            context_data: Additional context data to include in the prompt
            
        Returns:
            Generated content as string
        """
        if not self.ai_client:
            return f"[AI Content Generation Unavailable - Please configure AI client]\n{prompt}"
        
        try:
            # Prepare context
            context_str = ""
            if context_data:
                context_str = f"\n\nContext Data:\n{json.dumps(context_data, indent=2, default=str)}"
            
            # Customize prompt based on configuration
            style_instruction = self._get_style_instruction()
            detail_instruction = self._get_detail_instruction()
            
            full_prompt = f"""
You are an expert Azure migration consultant creating professional migration plan content.

{style_instruction}

{detail_instruction}

{prompt}

Requirements:
- Generate {self.config['content_style']} content suitable for enterprise migration plans
- Use specific data from the context when available
- Include concrete numbers, statistics, and actionable insights
- Structure content with clear sections and bullet points where appropriate
- Focus on practical, implementation-ready guidance
- Organization: {self.config['organization_name']}

{context_str}

Generate the content:
"""
            
            response = self.ai_client.chat.completions.create(
                model=self.config['ai_model'],
                messages=[
                    {"role": "system", "content": "You are an expert Azure migration consultant with deep knowledge of enterprise cloud migrations."},
                    {"role": "user", "content": full_prompt}
                ],
                max_tokens=self.config['ai_max_tokens'],
                temperature=self.config['ai_temperature']
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"[AI Content Generation Error: {str(e)}]\n\nFallback content for: {prompt}"
    
    def _get_style_instruction(self) -> str:
        """Get style instruction based on configuration."""
        style_instructions = {
            "professional": "Write in a professional, business-appropriate tone suitable for enterprise stakeholders.",
            "technical": "Focus on technical details and implementation specifics for IT professionals.",
            "executive": "Write in a high-level, strategic tone suitable for executive leadership and decision makers."
        }
        return style_instructions.get(self.config['content_style'], style_instructions['professional'])
    
    def _get_detail_instruction(self) -> str:
        """Get detail level instruction based on configuration."""
        detail_instructions = {
            "summary": "Provide concise, high-level information focusing on key points only.",
            "standard": "Provide balanced detail with essential information and supporting details.",
            "comprehensive": "Provide thorough, detailed analysis with comprehensive coverage of all aspects."
        }
        return detail_instructions.get(self.config['detail_level'], detail_instructions['comprehensive'])
    
    def generate_migration_plan(
        self, 
        azure_migrate_data: AzureMigrateReport,
        transcript_insights: List[QuestionAnswer],
        project_name: str = None
    ) -> AzureMigrationPlan:
        """
        Generate a comprehensive Azure Migration Plan document.
        
        Args:
            azure_migrate_data: Parsed Azure Migrate report data
            transcript_insights: Q&A insights from transcript analysis
            project_name: Name of the migration project (uses .env DEFAULT_PROJECT_NAME if None)
            
        Returns:
            Complete Azure Migration Plan document
        """
        
        # Use configured project name if none provided
        if project_name is None:
            project_name = self.config['default_project_name']
        
        # Generate executive summary and business case
        executive_summary = self._generate_executive_summary(azure_migrate_data, project_name)
        business_case = self._generate_business_case(azure_migrate_data, transcript_insights)
        
        # Analyze current infrastructure
        current_infrastructure = self._analyze_current_infrastructure(azure_migrate_data)
        
        # Generate target services analysis (simplified without architecture diagram)
        target_services = self._analyze_target_services_simplified(azure_migrate_data)
        
        # Create migration waves
        migration_waves = self._create_migration_waves(azure_migrate_data.servers, transcript_insights)
        
        # Generate timeline
        migration_timeline = self._generate_migration_timeline(migration_waves)
        
        # Assess risks (conditional based on config)
        risks = []
        if self.config['include_risk_assessment']:
            risks = self._assess_migration_risks(azure_migrate_data, migration_waves, transcript_insights)
        
        # Calculate cost estimates (conditional based on config)
        cost_estimates = []
        if self.config['include_cost_analysis']:
            cost_estimates = self._calculate_cost_estimates(azure_migrate_data, migration_waves)
        
        # Generate implementation plans
        resource_plan = self._generate_resource_plan(migration_waves, azure_migrate_data)
        training_plan = self._generate_training_plan(target_services, transcript_insights)
        communication_plan = self._generate_communication_plan(migration_timeline)
        
        # Define governance and compliance
        security_requirements = self._define_security_requirements(transcript_insights)
        compliance_requirements = self._define_compliance_requirements(transcript_insights)
        governance_model = self._define_governance_model(transcript_insights)
        
        # Generate success metrics
        kpis = self._generate_kpis(azure_migrate_data, cost_estimates)
        success_criteria = self._generate_success_criteria(migration_waves, transcript_insights)
        
        # Create technical specifications (conditional based on config)
        technical_specifications = {}
        if self.config['include_technical_details']:
            technical_specifications = self._generate_technical_specifications(azure_migrate_data)
        
        # Identify vendor requirements (conditional based on config)
        vendor_requirements = []
        if self.config['include_vendor_recommendations']:
            vendor_requirements = self._identify_vendor_requirements(target_services, transcript_insights)
        
        # Calculate totals
        total_investment = sum(ce.one_time_migration_cost + ce.azure_monthly_cost * 12 for ce in cost_estimates)
        expected_savings = sum(ce.annual_savings for ce in cost_estimates)
        
        return AzureMigrationPlan(
            project_name=project_name,
            executive_summary=executive_summary,
            business_case=business_case,
            current_infrastructure=current_infrastructure,
            azure_migrate_data=azure_migrate_data,
            target_services=target_services,
            migration_approach=self._determine_migration_approach(azure_migrate_data, transcript_insights),
            migration_timeline=migration_timeline,
            migration_waves=migration_waves,
            risks=risks,
            assumptions=self._generate_assumptions(transcript_insights),
            constraints=self._generate_constraints(transcript_insights),
            cost_estimates=cost_estimates,
            total_investment=total_investment,
            expected_savings=expected_savings,
            resource_plan=resource_plan,
            training_plan=training_plan,
            communication_plan=communication_plan,
            security_requirements=security_requirements,
            compliance_requirements=compliance_requirements,
            governance_model=governance_model,
            kpis=kpis,
            success_criteria=success_criteria,
            technical_specifications=technical_specifications,
            vendor_requirements=vendor_requirements
        )
    
    def _generate_executive_summary(self, azure_migrate_data: AzureMigrateReport, project_name: str) -> str:
        """Generate AI-driven executive summary section."""
        # Prepare data for AI context
        total_servers = len(azure_migrate_data.servers)
        ready_servers = len([s for s in azure_migrate_data.servers if 'ready' in s.readiness.lower()])
        
        # Calculate key metrics
        total_cost = sum(server.estimated_cost for server in azure_migrate_data.servers)
        os_breakdown = {}
        readiness_breakdown = {}
        
        for server in azure_migrate_data.servers:
            # OS distribution
            os_key = server.operating_system or "Unknown"
            os_breakdown[os_key] = os_breakdown.get(os_key, 0) + 1
            
            # Readiness distribution
            readiness_key = server.readiness or "Unknown"
            readiness_breakdown[readiness_key] = readiness_breakdown.get(readiness_key, 0) + 1
        
        context_data = {
            "project_name": project_name,
            "total_servers": total_servers,
            "ready_servers": ready_servers,
            "readiness_percentage": (ready_servers/total_servers*100) if total_servers > 0 else 0,
            "estimated_monthly_cost": total_cost,
            "os_distribution": os_breakdown,
            "readiness_breakdown": readiness_breakdown,
            "total_cpu_cores": sum(s.cpu_cores for s in azure_migrate_data.servers),
            "total_memory_gb": sum(s.memory_gb for s in azure_migrate_data.servers),
            "total_storage_gb": sum(s.disk_size_gb for s in azure_migrate_data.servers),
            "applications_identified": sum(len(s.applications) for s in azure_migrate_data.servers)
        }
        
        prompt = f"""
Create an executive summary for the Azure migration project '{project_name}'. 

The executive summary should include:
1. Project overview and scope
2. Key migration statistics and readiness assessment
3. Infrastructure scale and complexity analysis
4. Strategic objectives and expected benefits
5. High-level timeline and approach
6. Business value proposition

Use the provided context data to create specific, data-driven content. Include concrete numbers and percentages where relevant.
Make it compelling for executive stakeholders while being technically accurate.
"""
        
        return self._generate_ai_content(prompt, context_data)
    
    def _generate_business_case(self, azure_migrate_data: AzureMigrateReport, transcript_insights: List[QuestionAnswer]) -> str:
        """Generate AI-driven business case section."""
        total_monthly_cost = sum(server.estimated_cost for server in azure_migrate_data.servers)
        
        # Extract insights from transcript
        business_drivers = []
        pain_points = []
        compliance_requirements = []
        
        for qa in transcript_insights:
            question_lower = qa.question.lower()
            answer_lower = qa.answer.lower() if qa.answer else ""
            
            if any(keyword in question_lower for keyword in ['business', 'benefit', 'driver', 'reason', 'why', 'goal']):
                if qa.answer and len(qa.answer) > 10:
                    business_drivers.append(qa.answer)
            
            if any(keyword in question_lower for keyword in ['problem', 'issue', 'challenge', 'pain', 'difficulty']):
                if qa.answer and len(qa.answer) > 10:
                    pain_points.append(qa.answer)
                    
            if any(keyword in question_lower for keyword in ['compliance', 'regulation', 'audit', 'security', 'governance']):
                if qa.answer and len(qa.answer) > 10:
                    compliance_requirements.append(qa.answer)
        
        # Calculate infrastructure metrics
        server_ages = []
        legacy_systems = 0
        for server in azure_migrate_data.servers:
            if any(old_os in server.operating_system.lower() for old_os in ['2008', '2012', 'xp', 'vista']):
                legacy_systems += 1
        
        context_data = {
            "total_servers": len(azure_migrate_data.servers),
            "estimated_monthly_cost": total_monthly_cost,
            "annual_cost_estimate": total_monthly_cost * 12,
            "business_drivers": business_drivers[:5],  # Top 5
            "pain_points": pain_points[:5],
            "compliance_requirements": compliance_requirements,
            "legacy_systems_count": legacy_systems,
            "legacy_percentage": (legacy_systems / len(azure_migrate_data.servers) * 100) if azure_migrate_data.servers else 0,
            "total_cpu_cores": sum(s.cpu_cores for s in azure_migrate_data.servers),
            "total_memory_gb": sum(s.memory_gb for s in azure_migrate_data.servers),
            "applications_count": sum(len(s.applications) for s in azure_migrate_data.servers),
            "readiness_stats": {
                "ready": len([s for s in azure_migrate_data.servers if 'ready' in s.readiness.lower()]),
                "not_ready": len([s for s in azure_migrate_data.servers if 'not ready' in s.readiness.lower()]),
                "conditional": len([s for s in azure_migrate_data.servers if 'conditional' in s.readiness.lower()])
            }
        }
        
        prompt = """
Create a comprehensive business case for Azure migration that includes:

1. Executive Summary of Business Need
2. Current State Challenges and Pain Points
3. Financial Benefits Analysis
   - Cost savings opportunities
   - ROI projections
   - Capital vs operational expenditure analysis
4. Strategic Benefits
   - Business agility improvements
   - Innovation enablement
   - Competitive advantages
5. Risk Mitigation
   - Infrastructure modernization benefits
   - Security and compliance improvements
   - Business continuity enhancements
6. Implementation Investment
   - Migration costs
   - Timeline considerations
   - Resource requirements

Use the provided data to create specific, quantified benefits. Include percentage improvements, cost figures, and timeline estimates based on the infrastructure assessment data.
Focus on business value and ROI to justify the migration investment.
"""
        
        return self._generate_ai_content(prompt, context_data)
    
    def _analyze_current_infrastructure(self, azure_migrate_data: AzureMigrateReport) -> Dict[str, Any]:
        """Analyze current infrastructure state."""
        servers = azure_migrate_data.servers
        
        os_distribution = {}
        cpu_distribution = {}
        memory_distribution = {}
        
        for server in servers:
            # OS distribution
            os_key = server.operating_system if server.operating_system else "Unknown"
            os_distribution[os_key] = os_distribution.get(os_key, 0) + 1
            
            # CPU distribution
            cpu_range = self._get_cpu_range(server.cpu_cores)
            cpu_distribution[cpu_range] = cpu_distribution.get(cpu_range, 0) + 1
            
            # Memory distribution
            memory_range = self._get_memory_range(server.memory_gb)
            memory_distribution[memory_range] = memory_distribution.get(memory_range, 0) + 1
        
        total_cpu_cores = sum(server.cpu_cores for server in servers)
        total_memory_gb = sum(server.memory_gb for server in servers)
        total_storage_gb = sum(server.disk_size_gb for server in servers)
        
        return {
            "total_servers": len(servers),
            "total_cpu_cores": total_cpu_cores,
            "total_memory_gb": total_memory_gb,
            "total_storage_gb": total_storage_gb,
            "os_distribution": os_distribution,
            "cpu_distribution": cpu_distribution,
            "memory_distribution": memory_distribution,
            "average_cpu_per_server": total_cpu_cores / len(servers) if servers else 0,
            "average_memory_per_server": total_memory_gb / len(servers) if servers else 0,
            "average_storage_per_server": total_storage_gb / len(servers) if servers else 0
        }
    
    def _analyze_target_services(self, architecture_diagram: ArchitectureDiagram, azure_migrate_data: AzureMigrateReport) -> List[Dict[str, Any]]:
        """Analyze target Azure services."""
        service_analysis = []
        
        # Group components by Azure service type
        service_groups = {}
        for component in architecture_diagram.components:
            service_type = component.azure_service
            if service_type not in service_groups:
                service_groups[service_type] = []
            service_groups[service_type].append(component)
        
        for service_type, components in service_groups.items():
            analysis = {
                "service_name": service_type,
                "component_count": len(components),
                "migration_strategy": self._determine_service_migration_strategy(service_type),
                "benefits": self._get_service_benefits(service_type),
                "considerations": self._get_service_considerations(service_type),
                "estimated_effort": self._estimate_service_effort(service_type, len(components)),
                "components": [comp.name for comp in components]
            }
            service_analysis.append(analysis)
        
        return service_analysis
    
    def _analyze_target_services_simplified(self, azure_migrate_data: AzureMigrateReport) -> List[Dict[str, Any]]:
        """Analyze target Azure services based on current infrastructure."""
        service_analysis = []
        
        # Analyze what Azure services would be needed based on current servers
        for server in azure_migrate_data.servers:
            # Determine primary Azure service for this server
            primary_service = "Azure Virtual Machines"  # Default for lift-and-shift
            
            # Check for database workloads
            if any(app.lower() in ['sql', 'database', 'mysql', 'postgres'] for app in server.applications):
                service_analysis.append({
                    "service_name": "Azure SQL Database",
                    "migration_strategy": "Modernize",
                    "benefits": ["Managed service", "Built-in backup", "High availability"],
                    "considerations": ["Application compatibility", "Feature parity"],
                    "estimated_effort": "Medium",
                    "source_servers": [server.server_name]
                })
            
            # Check for web applications
            if any(app.lower() in ['iis', 'web', 'http', 'apache', 'nginx'] for app in server.applications):
                service_analysis.append({
                    "service_name": "Azure App Service",
                    "migration_strategy": "Modernize",
                    "benefits": ["Auto-scaling", "Integrated CI/CD", "Built-in load balancing"],
                    "considerations": ["Application dependencies", "Configuration changes"],
                    "estimated_effort": "Medium",
                    "source_servers": [server.server_name]
                })
            
            # Default VM service for all servers
            if not any(existing['service_name'] == primary_service for existing in service_analysis):
                service_analysis.append({
                    "service_name": primary_service,
                    "migration_strategy": "Lift-and-Shift",
                    "benefits": ["Quick migration", "Minimal changes", "Cost effective"],
                    "considerations": ["OS compatibility", "Performance optimization"],
                    "estimated_effort": "Low",
                    "source_servers": [s.server_name for s in azure_migrate_data.servers]
                })
        
        # Add common supporting services
        service_analysis.extend([
            {
                "service_name": "Azure Virtual Network",
                "migration_strategy": "New Implementation",
                "benefits": ["Network isolation", "Hybrid connectivity", "Security"],
                "considerations": ["IP addressing", "Subnet design", "Security groups"],
                "estimated_effort": "Low",
                "source_servers": []
            },
            {
                "service_name": "Azure Storage",
                "migration_strategy": "New Implementation", 
                "benefits": ["Scalable storage", "Multiple access tiers", "Geo-redundancy"],
                "considerations": ["Storage type selection", "Access patterns", "Cost optimization"],
                "estimated_effort": "Low",
                "source_servers": []
            },
            {
                "service_name": "Azure Backup",
                "migration_strategy": "New Implementation",
                "benefits": ["Automated backup", "Long-term retention", "Point-in-time recovery"],
                "considerations": ["Backup policies", "Retention periods", "Recovery procedures"],
                "estimated_effort": "Low", 
                "source_servers": []
            }
        ])
        
        return service_analysis

    def _create_migration_waves(self, servers: List[AzureMigrateServer], transcript_insights: List[QuestionAnswer]) -> List[MigrationWave]:
        """Create migration waves based on complexity and dependencies."""
        waves = []
        
        # Categorize servers by complexity and readiness
        wave_1_servers = []  # Ready servers, low complexity
        wave_2_servers = []  # Ready servers, medium complexity
        wave_3_servers = []  # Servers requiring remediation
        
        for server in servers:
            complexity_score = self._calculate_server_complexity(server)
            
            if 'ready' in server.readiness.lower():
                if complexity_score <= 3:
                    wave_1_servers.append(server)
                else:
                    wave_2_servers.append(server)
            else:
                wave_3_servers.append(server)
        
        # Create waves
        if wave_1_servers:
            waves.append(MigrationWave(
                wave_number=1,
                name="Pilot Migration - Low Complexity Systems",
                description="Migration of ready servers with low complexity to validate processes and tools",
                servers=wave_1_servers,
                duration_weeks=4,
                dependencies=["Azure environment setup", "Network connectivity", "Migration tools"],
                risk_level="Low",
                estimated_cost=sum(s.estimated_cost * 0.5 for s in wave_1_servers),  # Setup costs
                prerequisites=[
                    "Azure subscription and governance setup",
                    "Network connectivity established",
                    "Migration tooling configured",
                    "Backup and recovery procedures validated"
                ],
                success_criteria=[
                    "All pilot servers migrated successfully",
                    "Performance baselines met or exceeded",
                    "No data loss during migration",
                    "Rollback procedures validated"
                ]
            ))
        
        if wave_2_servers:
            waves.append(MigrationWave(
                wave_number=2,
                name="Production Migration - Medium Complexity Systems",
                description="Migration of production servers with moderate complexity",
                servers=wave_2_servers,
                duration_weeks=8,
                dependencies=["Wave 1 completion", "Lessons learned integration"],
                risk_level="Medium",
                estimated_cost=sum(s.estimated_cost * 0.7 for s in wave_2_servers),
                prerequisites=[
                    "Wave 1 successfully completed",
                    "Migration procedures refined",
                    "Extended maintenance windows approved",
                    "Additional monitoring tools deployed"
                ],
                success_criteria=[
                    "All production servers migrated with <2hr downtime each",
                    "No business service interruptions",
                    "Performance optimization completed",
                    "Security configurations validated"
                ]
            ))
        
        if wave_3_servers:
            waves.append(MigrationWave(
                wave_number=3,
                name="Complex Systems Migration",
                description="Migration of servers requiring remediation and complex applications",
                servers=wave_3_servers,
                duration_weeks=12,
                dependencies=["Wave 2 completion", "Remediation activities", "Application modernization"],
                risk_level="High",
                estimated_cost=sum(s.estimated_cost * 1.2 for s in wave_3_servers),  # Higher costs for complexity
                prerequisites=[
                    "Application compatibility issues resolved",
                    "Legacy system dependencies addressed",
                    "Extended testing completed",
                    "Specialized migration tools configured"
                ],
                success_criteria=[
                    "All complex systems successfully migrated",
                    "Application performance optimized",
                    "Legacy integrations maintained",
                    "Technical debt reduction achieved"
                ]
            ))
        
        return waves
    
    def _calculate_server_complexity(self, server: AzureMigrateServer) -> int:
        """Calculate complexity score for a server (1-10 scale)."""
        complexity = 1
        
        # OS complexity
        if 'windows' in server.operating_system.lower():
            if '2008' in server.operating_system or '2012' in server.operating_system:
                complexity += 2  # Older OS requires more work
            else:
                complexity += 1
        else:
            complexity += 1  # Linux systems
        
        # Resource complexity
        if server.cpu_cores > 8:
            complexity += 1
        if server.memory_gb > 32:
            complexity += 1
        if server.disk_size_gb > 500:
            complexity += 1
        
        # Application complexity
        if server.applications:
            complexity += len(server.applications) // 2
        
        # Readiness issues
        if 'not ready' in server.readiness.lower() or 'conditionally ready' in server.readiness.lower():
            complexity += 3
        
        return min(complexity, 10)
    
    def _generate_migration_timeline(self, migration_waves: List[MigrationWave]) -> MigrationTimeline:
        """Generate overall migration timeline."""
        total_weeks = sum(wave.duration_weeks for wave in migration_waves) + 4  # Add buffer
        total_months = math.ceil(total_weeks / 4)
        
        # Generate key milestones
        milestones = [
            {"milestone": "Project Initiation", "date": "Week 0", "description": "Project kickoff and team mobilization"},
            {"milestone": "Azure Environment Setup", "date": "Week 2", "description": "Azure subscription and base infrastructure setup"},
            {"milestone": "Migration Tools Setup", "date": "Week 3", "description": "Migration tooling configuration and testing"},
        ]
        
        current_week = 4
        for wave in migration_waves:
            milestones.append({
                "milestone": f"{wave.name} Start",
                "date": f"Week {current_week}",
                "description": f"Begin {wave.name}"
            })
            current_week += wave.duration_weeks
            milestones.append({
                "milestone": f"{wave.name} Complete",
                "date": f"Week {current_week}",
                "description": f"Complete {wave.name}"
            })
        
        milestones.append({
            "milestone": "Project Closure",
            "date": f"Week {current_week + 2}",
            "description": "Project closure and knowledge transfer"
        })
        
        critical_path = [
            "Azure environment setup",
            "Network connectivity establishment",
            "Migration tool configuration",
            "Pilot migration execution",
            "Production migration execution",
            "Complex systems migration"
        ]
        
        resource_requirements = {
            "project_manager": "1 FTE for entire duration",
            "azure_architect": "1 FTE for setup phase, 0.5 FTE ongoing",
            "migration_engineer": "2-3 FTE during active migration phases",
            "application_owner": "0.5 FTE per application during migration",
            "security_specialist": "0.5 FTE for setup and validation",
            "network_engineer": "1 FTE for setup phase, on-call during migration"
        }
        
        return MigrationTimeline(
            total_duration_months=total_months,
            waves=migration_waves,
            key_milestones=milestones,
            critical_path=critical_path,
            resource_requirements=resource_requirements
        )
    
    def _assess_migration_risks(self, azure_migrate_data: AzureMigrateReport, migration_waves: List[MigrationWave], transcript_insights: List[QuestionAnswer]) -> List[MigrationRisk]:
        """Generate AI-driven migration risk assessment."""
        
        # Analyze current infrastructure for risk factors
        not_ready_servers = [s for s in azure_migrate_data.servers if 'not ready' in s.readiness.lower()]
        conditional_servers = [s for s in azure_migrate_data.servers if 'conditional' in s.readiness.lower()]
        legacy_systems = [s for s in azure_migrate_data.servers if any(old in s.operating_system.lower() for old in ['2008', '2012', 'xp'])]
        
        # Extract risk-related insights from transcript
        risk_concerns = []
        business_criticality = []
        compliance_issues = []
        
        for qa in transcript_insights:
            question_lower = qa.question.lower()
            
            if any(keyword in question_lower for keyword in ['risk', 'concern', 'worry', 'problem', 'issue']):
                if qa.answer and len(qa.answer) > 10:
                    risk_concerns.append(qa.answer)
                    
            if any(keyword in question_lower for keyword in ['critical', 'important', 'business', 'downtime']):
                if qa.answer and len(qa.answer) > 10:
                    business_criticality.append(qa.answer)
                    
            if any(keyword in question_lower for keyword in ['compliance', 'regulation', 'audit', 'security']):
                if qa.answer and len(qa.answer) > 10:
                    compliance_issues.append(qa.answer)
        
        # Calculate risk metrics
        high_risk_waves = [w for w in migration_waves if w.risk_level in ["High", "Critical"]]
        complex_applications = sum(len(s.applications) for s in azure_migrate_data.servers)
        
        context_data = {
            "total_servers": len(azure_migrate_data.servers),
            "not_ready_servers": len(not_ready_servers),
            "conditional_servers": len(conditional_servers),
            "legacy_systems": len(legacy_systems),
            "migration_waves_count": len(migration_waves),
            "high_risk_waves": len(high_risk_waves),
            "complex_applications": complex_applications,
            "risk_concerns": risk_concerns,
            "business_criticality": business_criticality,
            "compliance_issues": compliance_issues,
            "server_details": [
                {
                    "name": s.server_name,
                    "os": s.operating_system,
                    "readiness": s.readiness,
                    "applications": len(s.applications),
                    "warnings": s.warnings
                } for s in azure_migrate_data.servers[:10]  # Sample of servers
            ],
            "wave_details": [
                {
                    "name": w.name,
                    "risk_level": w.risk_level,
                    "server_count": len(w.servers),
                    "duration_weeks": w.duration_weeks
                } for w in migration_waves
            ]
        }
        
        prompt = """
Conduct a comprehensive risk assessment for the Azure migration project and generate specific migration risks.

Analyze the provided data and create risks covering these categories:
1. Technical Risks (compatibility, performance, integration)
2. Business Risks (operations, continuity, stakeholder)
3. Security Risks (data protection, access, compliance)
4. Operational Risks (skills, process, management)

For each risk, provide:
- Unique risk ID (format: CATEGORY-###, e.g., TECH-001)
- Detailed description of the risk
- Impact level (Low, Medium, High, Critical)
- Probability (Low, Medium, High)
- Specific mitigation strategies
- Risk owner/responsible party
- Risk category

Focus on data-driven risks based on the server assessment, readiness issues, and stakeholder concerns.
Be specific about the migration context and provide actionable mitigation strategies.

Return the response as a JSON array of risk objects with the structure:
{
    "risk_id": "TECH-001",
    "description": "detailed description",
    "impact": "High",
    "probability": "Medium", 
    "mitigation": "specific mitigation strategy",
    "owner": "responsible party",
    "category": "Technical"
}
"""
        
        generated_content = self._generate_ai_content(prompt, context_data)
        
        # Parse AI-generated risks
        risks = []
        try:
            # Try to parse JSON response
            import json
            risk_data = json.loads(generated_content)
            
            for risk_item in risk_data:
                if isinstance(risk_item, dict) and all(key in risk_item for key in ['risk_id', 'description', 'impact', 'probability', 'mitigation', 'owner', 'category']):
                    risks.append(MigrationRisk(
                        risk_id=risk_item['risk_id'],
                        description=risk_item['description'],
                        impact=risk_item['impact'],
                        probability=risk_item['probability'],
                        mitigation=risk_item['mitigation'],
                        owner=risk_item['owner'],
                        category=risk_item['category']
                    ))
                    
        except (json.JSONDecodeError, KeyError):
            # Fallback: parse text-based response or create default risks
            pass
        
        # If AI parsing failed, add some data-driven default risks
        if len(risks) == 0:
            # Technical risks based on readiness
            if not_ready_servers:
                risks.append(MigrationRisk(
                    risk_id="TECH-001",
                    description=f"{len(not_ready_servers)} servers are not ready for migration due to compatibility issues",
                    impact="High",
                    probability="High",
                    mitigation="Conduct detailed compatibility assessment and remediation plan",
                    owner="Technical Team",
                    category="Technical"
                ))
            
            # Business continuity risks
            if high_risk_waves:
                risks.append(MigrationRisk(
                    risk_id="BUS-001",
                    description="Business disruption during complex system migration",
                    impact="High",
                    probability="Medium",
                    mitigation="Implement comprehensive rollback procedures and extended maintenance windows",
                    owner="Business Owner",
                    category="Business"
                ))
            
            # Security risks
            risks.append(MigrationRisk(
                risk_id="SEC-001",
                description="Data exposure during migration process",
                impact="Critical",
                probability="Low",
                mitigation="Implement encryption in transit and at rest, conduct security assessments",
                owner="Security Team",
                category="Security"
            ))
            
            # Operational risks
            risks.append(MigrationRisk(
                risk_id="OPS-001",
                description="Skills gap in Azure technologies",
                impact="Medium",
                probability="Medium",
                mitigation="Conduct comprehensive training program and engage Azure consulting partners",
                owner="Operations Manager",
                category="Operational"
            ))
        
        return risks
    
    def _calculate_cost_estimates(self, azure_migrate_data: AzureMigrateReport, migration_waves: List[MigrationWave]) -> List[CostEstimate]:
        """Calculate comprehensive cost estimates."""
        cost_estimates = []
        
        # Compute costs
        total_azure_compute = sum(server.estimated_cost for server in azure_migrate_data.servers)
        compute_estimate = CostEstimate(
            category="Compute",
            current_monthly_cost=total_azure_compute * 1.3,  # Assume current is 30% higher
            azure_monthly_cost=total_azure_compute,
            one_time_migration_cost=len(azure_migrate_data.servers) * 500,  # $500 per server migration
            annual_savings=(total_azure_compute * 1.3 - total_azure_compute) * 12,
            roi_months=18,
            details={
                "total_servers": len(azure_migrate_data.servers),
                "average_monthly_cost_per_server": total_azure_compute / len(azure_migrate_data.servers) if azure_migrate_data.servers else 0
            }
        )
        cost_estimates.append(compute_estimate)
        
        # Storage costs
        total_storage_gb = sum(server.disk_size_gb for server in azure_migrate_data.servers)
        storage_monthly_cost = total_storage_gb * 0.05  # $0.05 per GB estimate
        storage_estimate = CostEstimate(
            category="Storage",
            current_monthly_cost=storage_monthly_cost * 1.2,
            azure_monthly_cost=storage_monthly_cost,
            one_time_migration_cost=total_storage_gb * 0.01,  # Data transfer costs
            annual_savings=(storage_monthly_cost * 1.2 - storage_monthly_cost) * 12,
            roi_months=24,
            details={
                "total_storage_gb": total_storage_gb,
                "cost_per_gb": 0.05
            }
        )
        cost_estimates.append(storage_estimate)
        
        # Network costs
        network_estimate = CostEstimate(
            category="Network",
            current_monthly_cost=2000,  # Estimate current network costs
            azure_monthly_cost=1500,   # Azure network costs
            one_time_migration_cost=10000,  # Network setup costs
            annual_savings=(2000 - 1500) * 12,
            roi_months=20,
            details={
                "vpn_gateway": 150,
                "load_balancer": 25,
                "data_transfer": 500
            }
        )
        cost_estimates.append(network_estimate)
        
        # Management and monitoring
        management_estimate = CostEstimate(
            category="Management",
            current_monthly_cost=1000,
            azure_monthly_cost=800,
            one_time_migration_cost=5000,
            annual_savings=(1000 - 800) * 12,
            roi_months=25,
            details={
                "azure_monitor": 300,
                "log_analytics": 200,
                "backup": 300
            }
        )
        cost_estimates.append(management_estimate)
        
        return cost_estimates
    
    def _get_cpu_range(self, cpu_cores: int) -> str:
        """Get CPU range category."""
        if cpu_cores <= 2:
            return "1-2 cores"
        elif cpu_cores <= 4:
            return "3-4 cores"
        elif cpu_cores <= 8:
            return "5-8 cores"
        else:
            return "8+ cores"
    
    def _get_memory_range(self, memory_gb: float) -> str:
        """Get memory range category."""
        if memory_gb <= 4:
            return "1-4 GB"
        elif memory_gb <= 8:
            return "5-8 GB"
        elif memory_gb <= 16:
            return "9-16 GB"
        elif memory_gb <= 32:
            return "17-32 GB"
        else:
            return "32+ GB"
    
    def _determine_migration_approach(self, azure_migrate_data: AzureMigrateReport, transcript_insights: List[QuestionAnswer]) -> str:
        """Determine overall migration approach using AI analysis."""
        
        # Prepare infrastructure analysis
        infrastructure_summary = self._prepare_infrastructure_summary(azure_migrate_data)
        business_insights = self._extract_business_insights(transcript_insights)
        
        # Analyze approach preferences from transcript
        approach_keywords = {
            "lift-and-shift": ["rehost", "lift", "shift", "minimal changes", "quick", "fast", "simple"],
            "modernize": ["modernize", "refactor", "paas", "platform", "optimize", "improve"],
            "rearchitect": ["rearchitect", "rebuild", "cloud-native", "containerize", "microservices", "serverless"]
        }
        
        approach_scores = {"lift-and-shift": 0, "modernize": 0, "rearchitect": 0}
        
        for qa in transcript_insights:
            content = (qa.question + " " + (qa.answer or "")).lower()
            for approach, keywords in approach_keywords.items():
                for keyword in keywords:
                    if keyword in content:
                        approach_scores[approach] += 1
        
        context_data = {
            "infrastructure_summary": infrastructure_summary,
            "business_insights": business_insights,
            "approach_preferences": approach_scores,
            "migration_readiness": {
                "ready_percentage": (infrastructure_summary["readiness_distribution"].get("Ready", 0) / infrastructure_summary["total_servers"] * 100) if infrastructure_summary["total_servers"] > 0 else 0,
                "complexity_breakdown": infrastructure_summary["server_complexity"],
                "legacy_systems": sum(1 for os_name in infrastructure_summary["os_distribution"] if any(old in os_name.lower() for old in ['2008', '2012', 'xp']))
            },
            "business_priorities": business_insights.get("business_drivers", []),
            "technical_constraints": business_insights.get("technical_requirements", []),
            "timeline_pressure": business_insights.get("timeline_constraints", [])
        }
        
        prompt = """
Analyze the migration data and determine the optimal migration approach strategy.

Consider these factors:
1. Infrastructure readiness and complexity
2. Business drivers and timeline requirements
3. Stakeholder preferences expressed in discussions
4. Technical constraints and capabilities
5. Risk tolerance and transformation goals

Available migration approaches:
- Lift-and-Shift (Rehost): Minimal changes, fastest migration
- Modernize (Refactor): Optimize for cloud, moderate transformation
- Rearchitect (Rebuild): Full cloud-native transformation

Provide a recommendation that includes:
1. Primary migration approach (and percentage focus)
2. Secondary approaches for specific workloads (if applicable)
3. Justification based on the analysis
4. Specific recommendations for different server categories

Format the response as a clear migration strategy statement with supporting rationale.
"""
        
        ai_response = self._generate_ai_content(prompt, context_data)
        
        # If AI fails, fall back to scoring-based approach
        if not ai_response or ai_response.startswith("[AI"):
            primary_approach = max(approach_scores, key=approach_scores.get) if any(approach_scores.values()) else "lift-and-shift"
            return f"Hybrid approach with primary focus on {primary_approach}"
        
        return ai_response
    
    def _generate_assumptions(self, transcript_insights: List[QuestionAnswer]) -> List[str]:
        """Generate AI-driven project assumptions."""
        # Extract relevant information from transcript
        infrastructure_details = []
        business_context = []
        technical_requirements = []
        
        for qa in transcript_insights:
            question_lower = qa.question.lower()
            
            if any(keyword in question_lower for keyword in ['infrastructure', 'network', 'connectivity', 'environment']):
                if qa.answer and len(qa.answer) > 10:
                    infrastructure_details.append(qa.answer)
            
            if any(keyword in question_lower for keyword in ['business', 'process', 'timeline', 'budget', 'resource']):
                if qa.answer and len(qa.answer) > 10:
                    business_context.append(qa.answer)
                    
            if any(keyword in question_lower for keyword in ['technical', 'application', 'system', 'requirement']):
                if qa.answer and len(qa.answer) > 10:
                    technical_requirements.append(qa.answer)
        
        context_data = {
            "infrastructure_details": infrastructure_details,
            "business_context": business_context,
            "technical_requirements": technical_requirements,
            "qa_insights": [{"question": qa.question, "answer": qa.answer} for qa in transcript_insights[:10]]
        }
        
        prompt = """
Generate a comprehensive list of project assumptions for the Azure migration. 

Create assumptions covering:
1. Infrastructure and Technical Assumptions
2. Business and Organizational Assumptions  
3. Security and Compliance Assumptions
4. Timeline and Resource Assumptions
5. Financial and Budgetary Assumptions

Each assumption should be:
- Specific and actionable
- Based on the provided context where possible
- Realistic for enterprise migration projects
- Clear about dependencies and prerequisites

Return the assumptions as a Python list of strings, with each assumption being a clear, complete sentence.
Format: Return only the list, no additional text.
"""
        
        generated_content = self._generate_ai_content(prompt, context_data)
        
        # Parse the generated content to extract list items
        try:
            # Try to extract assumptions from the generated content
            lines = generated_content.split('\n')
            assumptions = []
            
            for line in lines:
                line = line.strip()
                if line and (line.startswith('•') or line.startswith('-') or line.startswith('*')):
                    assumptions.append(line.lstrip('•-*').strip())
                elif line and len(line) > 20 and not line.startswith('['):  # Skip headers and short lines
                    assumptions.append(line)
            
            # If we couldn't parse properly, return fallback assumptions
            if len(assumptions) < 5:
                assumptions = [
                    "Azure subscription and necessary permissions will be available",
                    "Network connectivity between on-premises and Azure will be established",
                    "Business stakeholders will provide necessary approvals for maintenance windows",
                    "Sufficient budget allocation for migration tools and Azure resources",
                    "Technical team will receive appropriate Azure training",
                    "Current server performance baselines are representative of production load",
                    "No major application changes will be required during migration timeframe"
                ]
                
            return assumptions[:15]  # Limit to 15 assumptions
            
        except Exception:
            # Fallback to default assumptions
            return [
                "Azure subscription and necessary permissions will be available",
                "Network connectivity between on-premises and Azure will be established",
                "Business stakeholders will provide necessary approvals for maintenance windows",
                "Sufficient budget allocation for migration tools and Azure resources",
                "Technical team will receive appropriate Azure training"
            ]
    
    def _generate_constraints(self, transcript_insights: List[QuestionAnswer]) -> List[str]:
        """Generate AI-driven project constraints."""
        # Extract constraint-related information from transcript
        business_constraints = []
        technical_constraints = []
        compliance_constraints = []
        timeline_constraints = []
        
        for qa in transcript_insights:
            question_lower = qa.question.lower()
            answer_lower = qa.answer.lower() if qa.answer else ""
            
            if any(keyword in question_lower for keyword in ['constraint', 'limitation', 'restriction', 'cannot', 'must not']):
                if qa.answer and len(qa.answer) > 10:
                    business_constraints.append(qa.answer)
            
            if any(keyword in question_lower for keyword in ['downtime', 'maintenance', 'window', 'availability']):
                if qa.answer and len(qa.answer) > 10:
                    timeline_constraints.append(qa.answer)
                    
            if any(keyword in question_lower for keyword in ['compliance', 'regulation', 'audit', 'security', 'policy']):
                if qa.answer and len(qa.answer) > 10:
                    compliance_constraints.append(qa.answer)
                    
            if any(keyword in question_lower for keyword in ['technical', 'system', 'application', 'dependency']):
                if qa.answer and len(qa.answer) > 10:
                    technical_constraints.append(qa.answer)
        
        context_data = {
            "business_constraints": business_constraints,
            "technical_constraints": technical_constraints,
            "compliance_constraints": compliance_constraints,
            "timeline_constraints": timeline_constraints,
            "all_qa_insights": [{"question": qa.question, "answer": qa.answer} for qa in transcript_insights if qa.answer]
        }
        
        prompt = """
Generate a comprehensive list of project constraints for the Azure migration project.

Create constraints covering:
1. Business and Operational Constraints
2. Technical and System Constraints  
3. Security and Compliance Constraints
4. Timeline and Resource Constraints
5. Financial and Budgetary Constraints

Each constraint should be:
- Specific and measurable where possible
- Based on the provided context and insights
- Realistic for enterprise environments
- Clear about limitations and restrictions

Focus on constraints that will impact the migration project planning, execution, and success.
Return the constraints as a Python list of strings, with each constraint being a clear, complete sentence.
Format: Return only the list, no additional text.
"""
        
        generated_content = self._generate_ai_content(prompt, context_data)
        
        # Parse the generated content to extract constraint items
        try:
            lines = generated_content.split('\n')
            constraints = []
            
            for line in lines:
                line = line.strip()
                if line and (line.startswith('•') or line.startswith('-') or line.startswith('*')):
                    constraints.append(line.lstrip('•-*').strip())
                elif line and len(line) > 20 and not line.startswith('['):  # Skip headers and short lines
                    constraints.append(line)
            
            # If we couldn't parse properly, return fallback constraints with extracted insights
            if len(constraints) < 3:
                constraints = [
                    "Limited maintenance windows for production systems",
                    "Compliance requirements must be maintained throughout migration",
                    "No data loss tolerance for critical business applications"
                ]
                
                # Add specific constraints from transcript
                for qa in transcript_insights:
                    if any(keyword in qa.question.lower() for keyword in ['constraint', 'limitation', 'requirement', 'compliance']):
                        if qa.answer and len(qa.answer) > 10:
                            constraints.append(qa.answer)
                            
            return constraints[:10]  # Limit to top 10
            
        except Exception:
            # Fallback constraints
            fallback_constraints = [
                "Limited maintenance windows for production systems",
                "Compliance requirements must be maintained throughout migration",
                "No data loss tolerance for critical business applications"
            ]
            
            # Add specific constraints from transcript
            for qa in transcript_insights:
                if any(keyword in qa.question.lower() for keyword in ['constraint', 'limitation', 'requirement', 'compliance']):
                    if qa.answer and len(qa.answer) > 10:
                        fallback_constraints.append(qa.answer)
                        
            return fallback_constraints[:10]
    
    def _generate_resource_plan(self, migration_waves: List[MigrationWave], azure_migrate_data: AzureMigrateReport) -> Dict[str, Any]:
        """Generate resource allocation plan."""
        return {
            "project_team": {
                "project_manager": {
                    "role": "Project Manager",
                    "duration": "Full project duration",
                    "responsibilities": ["Overall project coordination", "Stakeholder management", "Risk management"]
                },
                "azure_architect": {
                    "role": "Azure Solution Architect",
                    "duration": "Full project duration",
                    "responsibilities": ["Architecture design", "Azure best practices", "Technical governance"]
                },
                "migration_engineers": {
                    "role": "Migration Engineers",
                    "count": len(migration_waves),
                    "duration": "Active migration phases",
                    "responsibilities": ["Server migration execution", "Testing and validation", "Issue resolution"]
                }
            },
            "training_requirements": {
                "azure_fundamentals": "All technical team members",
                "azure_administration": "Operations team",
                "azure_security": "Security team",
                "migration_tools": "Migration engineers"
            },
            "external_resources": {
                "azure_consulting": "Architecture review and best practices",
                "migration_tools": "Azure Migrate, third-party tools as needed",
                "training_provider": "Microsoft or certified Azure training partner"
            }
        }
    
    def _generate_training_plan(self, target_services: List[Dict[str, Any]], transcript_insights: List[QuestionAnswer]) -> Dict[str, Any]:
        """Generate AI-driven comprehensive training plan."""
        
        # Extract training-related insights
        skill_gaps = []
        team_details = []
        current_expertise = []
        
        for qa in transcript_insights:
            question_lower = qa.question.lower()
            
            if any(keyword in question_lower for keyword in ['skill', 'training', 'knowledge', 'experience', 'expertise']):
                if qa.answer and len(qa.answer) > 10:
                    if any(gap_word in question_lower for gap_word in ['gap', 'lack', 'need', 'missing']):
                        skill_gaps.append(qa.answer)
                    else:
                        current_expertise.append(qa.answer)
                        
            if any(keyword in question_lower for keyword in ['team', 'staff', 'people', 'resource', 'role']):
                if qa.answer and len(qa.answer) > 10:
                    team_details.append(qa.answer)
        
        # Analyze Azure services for training requirements
        azure_services = set()
        migration_complexity = "Medium"
        
        for service in target_services:
            service_name = service.get("service_name", "")
            azure_services.add(service_name)
            
            # Assess complexity based on services
            if any(complex_service in service_name for complex_service in ["Kubernetes", "Container", "Functions", "Cosmos"]):
                migration_complexity = "High"
        
        context_data = {
            "target_azure_services": list(azure_services),
            "migration_complexity": migration_complexity,
            "skill_gaps_identified": skill_gaps,
            "current_team_expertise": current_expertise,
            "team_details": team_details,
            "service_analysis": target_services,
            "total_services": len(target_services),
            "training_categories_needed": list(set([
                service.get("migration_strategy", "lift-and-shift") for service in target_services
            ]))
        }
        
        prompt = """
Create a comprehensive training plan for the Azure migration project team.

Design training programs covering:
1. Azure Fundamentals (for all team members)
2. Azure Administration and Operations 
3. Migration-Specific Tools and Processes
4. Service-Specific Training (based on target Azure services)
5. Security and Compliance Training
6. Ongoing Enablement and Knowledge Transfer

For each training program, specify:
- Target audience and prerequisites
- Duration and delivery method
- Detailed learning objectives and content outline
- Hands-on labs and practical exercises
- Assessment and certification requirements
- Timeline and scheduling considerations
- Training providers and resources

Consider the current skill gaps, team expertise, and complexity of the target Azure services.
Create a realistic timeline that supports the migration project schedule.

Return the response as a structured JSON object with training programs as keys.
"""
        
        generated_content = self._generate_ai_content(prompt, context_data)
        
        # Try to parse AI response, fallback to structured default if needed
        try:
            import json
            training_plan = json.loads(generated_content)
            
            # Validate the structure
            if isinstance(training_plan, dict) and len(training_plan) > 0:
                return training_plan
                
        except (json.JSONDecodeError, TypeError):
            pass
        
        # Fallback to enhanced default training plan
        return {
            "azure_fundamentals": {
                "target_audience": "All project team members",
                "duration": "2 days",
                "delivery": "Instructor-led or online",
                "content": ["Azure basics", "Core services", "Pricing and support"],
                "prerequisites": "Basic IT infrastructure knowledge",
                "certification": "Azure Fundamentals (AZ-900)"
            },
            "azure_administration": {
                "target_audience": "IT Operations team",
                "duration": "5 days",
                "delivery": "Hands-on workshop",
                "content": ["Resource management", "Monitoring and alerts", "Security configuration"],
                "prerequisites": "Azure Fundamentals completion",
                "certification": "Azure Administrator Associate (AZ-104)"
            },
            "migration_specific": {
                "target_audience": "Migration team",
                "duration": "3 days", 
                "delivery": "Hands-on workshop",
                "content": ["Azure Migrate tools", "Migration best practices", "Troubleshooting"],
                "prerequisites": "Azure administration basics",
                "certification": "Hands-on migration certification"
            },
            "service_specific": {
                "target_audience": "Technical specialists",
                "duration": "Variable based on services",
                "delivery": "Targeted workshops",
                "content": [f"Training for {service}" for service in azure_services],
                "prerequisites": "Service-specific knowledge",
                "certification": "Service-specific certifications"
            },
            "ongoing_enablement": {
                "description": "Monthly knowledge sharing sessions",
                "duration": "2 hours per month",
                "content": "New Azure features, lessons learned, best practices",
                "target_audience": "All technical team members",
                "delivery": "Virtual sessions"
            }
        }
    
    def _generate_communication_plan(self, migration_timeline: MigrationTimeline) -> Dict[str, Any]:
        """Generate communication plan."""
        return {
            "stakeholder_meetings": {
                "executive_updates": {
                    "frequency": "Monthly",
                    "audience": "Executive sponsors",
                    "content": "High-level progress, risks, budget status"
                },
                "project_team_meetings": {
                    "frequency": "Weekly",
                    "audience": "Core project team",
                    "content": "Detailed progress, technical issues, next steps"
                },
                "business_updates": {
                    "frequency": "Bi-weekly",
                    "audience": "Business stakeholders",
                    "content": "Impact on business operations, upcoming changes"
                }
            },
            "communication_channels": {
                "project_portal": "Centralized project documentation and status",
                "email_updates": "Weekly progress emails to all stakeholders",
                "teams_channel": "Real-time communication for project team"
            },
            "change_management": {
                "user_communications": "Regular updates on system changes",
                "training_announcements": "Schedule and requirements for user training",
                "go_live_notifications": "Detailed communications for each migration wave"
            }
        }
    
    def _define_security_requirements(self, transcript_insights: List[QuestionAnswer]) -> List[str]:
        """Define security requirements."""
        requirements = [
            "Implement Azure Security Center for continuous security monitoring",
            "Enable Azure AD for identity and access management",
            "Configure Network Security Groups for network segmentation",
            "Implement Azure Key Vault for secrets management",
            "Enable encryption at rest and in transit for all data",
            "Configure Azure Backup for data protection",
            "Implement Azure Monitor for security event logging",
            "Conduct security assessment post-migration"
        ]
        
        # Extract specific security requirements from transcript
        for qa in transcript_insights:
            if any(keyword in qa.question.lower() for keyword in ['security', 'compliance', 'encryption', 'access']):
                if qa.answer and len(qa.answer) > 10:
                    requirements.append(qa.answer)
        
        return requirements[:15]  # Limit to top 15
    
    def _define_compliance_requirements(self, transcript_insights: List[QuestionAnswer]) -> List[str]:
        """Define compliance requirements."""
        requirements = [
            "Maintain data residency requirements",
            "Implement audit logging for compliance reporting",
            "Configure data retention policies",
            "Ensure GDPR compliance for EU data",
            "Implement proper access controls and segregation of duties"
        ]
        
        # Extract specific compliance requirements from transcript
        for qa in transcript_insights:
            if any(keyword in qa.question.lower() for keyword in ['compliance', 'regulation', 'audit', 'gdpr', 'hipaa']):
                if qa.answer and len(qa.answer) > 10:
                    requirements.append(qa.answer)
        
        return requirements
    
    def _define_governance_model(self, transcript_insights: List[QuestionAnswer]) -> Dict[str, Any]:
        """Define governance model."""
        return {
            "governance_structure": {
                "steering_committee": "Executive oversight and decision making",
                "project_management_office": "Project coordination and reporting",
                "technical_working_group": "Technical decisions and standards",
                "business_working_group": "Business requirements and validation"
            },
            "decision_authority": {
                "architectural_decisions": "Azure Architect with steering committee approval",
                "migration_schedule": "Project Manager with business approval",
                "scope_changes": "Steering committee",
                "technical_issues": "Technical working group"
            },
            "standards_and_policies": {
                "naming_conventions": "Azure resource naming standards",
                "security_policies": "Enterprise security requirements in Azure",
                "cost_management": "Budget controls and resource optimization",
                "change_management": "Formal change control process"
            }
        }
    
    def _generate_kpis(self, azure_migrate_data: AzureMigrateReport, cost_estimates: List[CostEstimate]) -> List[Dict[str, Any]]:
        """Generate key performance indicators."""
        return [
            {
                "kpi": "Migration Success Rate",
                "target": "99%",
                "measurement": "Percentage of servers successfully migrated",
                "frequency": "Per migration wave"
            },
            {
                "kpi": "Downtime per Server",
                "target": "<4 hours",
                "measurement": "Average downtime during migration",
                "frequency": "Per server migration"
            },
            {
                "kpi": "Cost Optimization",
                "target": "20% reduction",
                "measurement": "Monthly infrastructure cost reduction",
                "frequency": "Monthly post-migration"
            },
            {
                "kpi": "Performance Baseline",
                "target": "Meet or exceed",
                "measurement": "Application performance vs. baseline",
                "frequency": "Post-migration validation"
            },
            {
                "kpi": "Security Posture",
                "target": "Zero critical findings",
                "measurement": "Security assessment results",
                "frequency": "Post-migration security scan"
            }
        ]
    
    def _generate_success_criteria(self, migration_waves: List[MigrationWave], transcript_insights: List[QuestionAnswer]) -> List[str]:
        """Generate overall success criteria."""
        criteria = [
            "All in-scope servers successfully migrated to Azure",
            "No data loss during migration process",
            "Application performance meets or exceeds baseline",
            "Security and compliance requirements fully implemented",
            "Total project delivered within approved budget and timeline",
            "Team successfully trained on Azure operations",
            "Business operations continue without significant disruption"
        ]
        
        # Add wave-specific criteria
        for wave in migration_waves:
            criteria.extend([f"{wave.name}: " + criterion for criterion in wave.success_criteria])
        
        return criteria
    
    def _generate_technical_specifications(self, azure_migrate_data: AzureMigrateReport) -> Dict[str, Any]:
        """Generate technical specifications."""
        return {
            "network_architecture": {
                "virtual_networks": 1,  # Assume single VNet for simplicity
                "subnets": 3,  # Typical web/app/data tier setup
                "security_groups": len(azure_migrate_data.servers)  # One NSG per server minimum
            },
            "compute_specifications": {
                "total_servers": len(azure_migrate_data.servers),
                "total_cpu_cores": sum(s.cpu_cores for s in azure_migrate_data.servers),
                "total_memory_gb": sum(s.memory_gb for s in azure_migrate_data.servers),
                "total_storage_gb": sum(s.disk_size_gb for s in azure_migrate_data.servers)
            },
            "migration_tools": {
                "azure_migrate": "Primary assessment and migration tool",
                "azure_site_recovery": "Replication and failover",
                "azure_database_migration_service": "Database migrations",
                "azure_data_box": "Large data transfers if needed"
            }
        }
    
    def _identify_vendor_requirements(self, target_services: List[Dict[str, Any]], transcript_insights: List[QuestionAnswer]) -> List[str]:
        """Identify vendor and partner requirements."""
        requirements = [
            "Microsoft Azure subscription with appropriate service limits",
            "Azure support plan (Professional Direct or Premier recommended)",
            "Network service provider for ExpressRoute or VPN connectivity",
            "Azure Migrate licensing for assessment tools"
        ]
        
        # Add service-specific vendor requirements
        service_vendors = {
            "Azure SQL": "Microsoft SQL Server licensing considerations",
            "Azure AD": "Active Directory domain services integration",
            "Azure Backup": "Third-party backup tool migration planning"
        }
        
        for service in target_services:
            service_name = service.get("service_name", "")
            if service_name in service_vendors:
                requirements.append(service_vendors[service_name])
        
        return list(set(requirements))  # Remove duplicates
    
    def _determine_service_migration_strategy(self, service_type: str) -> str:
        """Determine migration strategy for Azure service."""
        strategies = {
            "Azure Virtual Machine": "Lift-and-shift",
            "Azure App Service": "Modernize",
            "Azure SQL Database": "Modernize",
            "Azure Container Instances": "Containerize",
            "Azure Kubernetes Service": "Rearchitect",
            "Azure Functions": "Rearchitect"
        }
        return strategies.get(service_type, "Lift-and-shift")
    
    def _get_service_benefits(self, service_type: str) -> List[str]:
        """Get benefits for Azure service."""
        benefits = {
            "Azure Virtual Machine": ["Familiar environment", "Minimal application changes", "Quick migration"],
            "Azure App Service": ["Managed platform", "Auto-scaling", "Built-in monitoring"],
            "Azure SQL Database": ["Managed service", "Built-in high availability", "Automatic backups"],
            "Azure Container Instances": ["Resource efficiency", "Fast startup", "Pay-per-second billing"],
            "Azure Kubernetes Service": ["Container orchestration", "Auto-scaling", "DevOps integration"]
        }
        return benefits.get(service_type, ["Cloud benefits", "Scalability", "Managed service"])
    
    def _get_service_considerations(self, service_type: str) -> List[str]:
        """Get considerations for Azure service."""
        considerations = {
            "Azure Virtual Machine": ["OS licensing costs", "Patching responsibility", "Limited auto-scaling"],
            "Azure App Service": ["Application compatibility", "Framework limitations", "Code changes may be required"],
            "Azure SQL Database": ["Feature compatibility", "Connection string changes", "Potential performance tuning"],
            "Azure Container Instances": ["Application containerization", "State management", "Networking complexity"],
            "Azure Kubernetes Service": ["Container expertise required", "Complex networking", "Operational overhead"]
        }
        return considerations.get(service_type, ["Cost optimization", "Security configuration", "Operational procedures"])
    
    def _estimate_service_effort(self, service_type: str, component_count: int) -> str:
        """Estimate effort for service migration."""
        base_efforts = {
            "Azure Virtual Machine": 2,  # days per VM
            "Azure App Service": 5,      # days per app
            "Azure SQL Database": 3,     # days per database
            "Azure Container Instances": 4,  # days per container group
            "Azure Kubernetes Service": 10   # days per cluster
        }
        
        base_effort = base_efforts.get(service_type, 3)
        total_days = base_effort * component_count
        
        if total_days <= 5:
            return "Low (< 1 week)"
        elif total_days <= 20:
            return "Medium (1-4 weeks)"
        elif total_days <= 60:
            return "High (1-3 months)"
        else:
            return "Very High (3+ months)"
    
    def _prepare_infrastructure_summary(self, azure_migrate_data: AzureMigrateReport) -> Dict[str, Any]:
        """Prepare a comprehensive summary of the infrastructure for AI context."""
        servers = azure_migrate_data.servers
        
        # OS distribution
        os_dist = {}
        readiness_dist = {}
        app_count_dist = {"0": 0, "1-3": 0, "4-10": 0, "10+": 0}
        complexity_dist = {"low": 0, "medium": 0, "high": 0}
        
        total_warnings = 0
        
        for server in servers:
            # OS distribution
            os_key = server.operating_system or "Unknown"
            os_dist[os_key] = os_dist.get(os_key, 0) + 1
            
            # Readiness distribution
            readiness_key = server.readiness or "Unknown"
            readiness_dist[readiness_key] = readiness_dist.get(readiness_key, 0) + 1
            
            # Application complexity
            app_count = len(server.applications)
            if app_count == 0:
                app_count_dist["0"] += 1
            elif app_count <= 3:
                app_count_dist["1-3"] += 1
            elif app_count <= 10:
                app_count_dist["4-10"] += 1
            else:
                app_count_dist["10+"] += 1
            
            # Server complexity
            complexity = self._calculate_server_complexity(server)
            if complexity <= 3:
                complexity_dist["low"] += 1
            elif complexity <= 6:
                complexity_dist["medium"] += 1
            else:
                complexity_dist["high"] += 1
                
            total_warnings += len(server.warnings)
        
        return {
            "total_servers": len(servers),
            "os_distribution": os_dist,
            "readiness_distribution": readiness_dist,
            "application_complexity": app_count_dist,
            "server_complexity": complexity_dist,
            "total_warnings": total_warnings,
            "infrastructure_totals": {
                "total_cpu_cores": sum(s.cpu_cores for s in servers),
                "total_memory_gb": sum(s.memory_gb for s in servers),
                "total_storage_gb": sum(s.disk_size_gb for s in servers),
                "total_estimated_cost": sum(s.estimated_cost for s in servers)
            },
            "top_warnings": self._get_top_warnings(servers),
            "critical_servers": [
                {"name": s.server_name, "readiness": s.readiness, "warnings": len(s.warnings)}
                for s in servers if 'not ready' in s.readiness.lower() or len(s.warnings) > 3
            ][:5]
        }
    
    def _get_top_warnings(self, servers: List[AzureMigrateServer]) -> List[str]:
        """Extract top warnings across all servers."""
        warning_counts = {}
        
        for server in servers:
            for warning in server.warnings:
                warning_counts[warning] = warning_counts.get(warning, 0) + 1
        
        # Sort by frequency and return top 10
        sorted_warnings = sorted(warning_counts.items(), key=lambda x: x[1], reverse=True)
        return [warning for warning, count in sorted_warnings[:10]]
    
    def _extract_business_insights(self, transcript_insights: List[QuestionAnswer]) -> Dict[str, List[str]]:
        """Extract categorized business insights from transcript."""
        insights = {
            "business_drivers": [],
            "pain_points": [],
            "compliance_requirements": [],
            "timeline_constraints": [],
            "budget_considerations": [],
            "technical_requirements": [],
            "security_concerns": [],
            "stakeholder_priorities": []
        }
        
        for qa in transcript_insights:
            if not qa.answer or len(qa.answer) < 10:
                continue
                
            question_lower = qa.question.lower()
            
            # Categorize based on question content
            if any(keyword in question_lower for keyword in ['business', 'benefit', 'driver', 'goal', 'objective']):
                insights["business_drivers"].append(qa.answer)
            elif any(keyword in question_lower for keyword in ['problem', 'issue', 'challenge', 'pain', 'difficulty']):
                insights["pain_points"].append(qa.answer)
            elif any(keyword in question_lower for keyword in ['compliance', 'regulation', 'audit', 'policy']):
                insights["compliance_requirements"].append(qa.answer)
            elif any(keyword in question_lower for keyword in ['timeline', 'schedule', 'deadline', 'when', 'time']):
                insights["timeline_constraints"].append(qa.answer)
            elif any(keyword in question_lower for keyword in ['budget', 'cost', 'money', 'funding', 'investment']):
                insights["budget_considerations"].append(qa.answer)
            elif any(keyword in question_lower for keyword in ['technical', 'technology', 'system', 'application']):
                insights["technical_requirements"].append(qa.answer)
            elif any(keyword in question_lower for keyword in ['security', 'secure', 'protection', 'access', 'encryption']):
                insights["security_concerns"].append(qa.answer)
            elif any(keyword in question_lower for keyword in ['priority', 'important', 'critical', 'key', 'essential']):
                insights["stakeholder_priorities"].append(qa.answer)
        
        # Limit each category to top 5 items
        for category in insights:
            insights[category] = insights[category][:5]
            
        return insights
