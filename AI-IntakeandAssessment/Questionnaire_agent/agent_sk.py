import os
import asyncio
import re
import json
from typing import Optional, List
from semantic_kernel import Kernel
from semantic_kernel.agents import AzureAIAgent, AzureAIAgentSettings, AzureAIAgentThread
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from azure.identity.aio import DefaultAzureCredential as AsyncDefaultAzureCredential
from azure.identity import AzureCliCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import ConnectionType

from plugins_refactored import QuestionnaireProcessorPlugin, BlobPlugin, ReviewPlugin
from tools.excel import _parse_sheet_names
from tools.telemetry import TelemetryLogger

# New imports for agent tools
from azure.ai.agents.models import (
    AzureAISearchTool,
    AzureAISearchQueryType,
    OpenApiTool,
    OpenApiAnonymousAuthDetails,
    ToolResources,
    ConnectedAgentTool,
)


class QuestionnaireAgentSK:
    """Semantic Kernel-based Questionnaire Agent with proper kernel initialization"""
    
    def __init__(self, app_id: str):
        self.app_id = app_id
        self.verbose = os.getenv("ASSESS_DEBUG", "0") in ("1", "true", "True", "yes")
        self.telemetry = TelemetryLogger()
        self.kernel: Optional[Kernel] = None
        self.agent: Optional[AzureAIAgent] = None
        self.client = None
        
        # Validate environment
        self._validate_environment()
        
    def _validate_environment(self):
        """Validate required environment variables"""
        self.endpoint = os.getenv("AZURE_AI_AGENT_ENDPOINT")
        self.model_deployment = os.getenv("AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME")
        self.search_index = os.getenv("AZURE_SEARCH_INDEX")
        # Prefer direct connection id provided by user
        self.search_connection_id = os.getenv("AZURE_SEARCH_CONNECTION_ID")
        # Optional: name fallback (not used unless you add resolver)
        self.search_connection = os.getenv("AZURE_SEARCH_CONNECTION_NAME")
        # Function App config
        self.func_base_url = os.getenv("FUNC_BASE_URL")  # e.g., https://<app>.azurewebsites.net
        self.func_api_key = os.getenv("FUNC_API_KEY")
        self.target_sheets = _parse_sheet_names(os.getenv("EXCEL_SHEETS"))
        # Connected Agent B config
        self.connected_agent_b_id = os.getenv("CONNECTED_AGENT_B_ID")
        self.connected_agent_b_name = os.getenv("CONNECTED_AGENT_B_NAME") or "search_agent_b"
        self.connected_agent_b_desc = os.getenv("CONNECTED_AGENT_B_DESC") or (
            "Delegated retrieval agent that answers questions using Azure AI Search and returns compact JSON."
        )
        # Allow disabling main agent's own Search tool to force delegation
        self.disable_a_search_tool = os.getenv("DISABLE_A_SEARCH_TOOL", "0") in ("1", "true", "True", "yes")
        
        missing = []
        if not self.endpoint:
            missing.append("AZURE_AI_AGENT_ENDPOINT")
        if not self.model_deployment:
            missing.append("AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME")
        if not self.search_index:
            missing.append("AZURE_SEARCH_INDEX")
        if not self.search_connection_id and not self.connected_agent_b_id:
            # If no local search tool and no connected agent, we can't retrieve answers
            missing.append("AZURE_SEARCH_CONNECTION_ID or CONNECTED_AGENT_B_ID")
        if missing:
            raise RuntimeError(f"Missing required env vars: {', '.join(missing)}")
    
    def _vprint(self, msg: str):
        """Verbose print for debugging"""
        if self.verbose:
            print(f"[SK Agent] {msg}")
    
    async def initialize_kernel(self) -> Kernel:
        """Initialize Semantic Kernel with plugins"""
        if self.kernel:
            return self.kernel
            
        self._vprint("Initializing Semantic Kernel...")
        
        # Create kernel instance
        self.kernel = Kernel()
        
        # Add Azure OpenAI service (if using direct kernel execution)
        if os.getenv("AZURE_OPENAI_ENDPOINT") and os.getenv("AZURE_OPENAI_API_KEY"):
            service_id = "questionnaire_service"
            self.kernel.add_service(
                AzureChatCompletion(
                    service_id=service_id,
                    deployment_name=self.model_deployment,
                    endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                )
            )
            self._vprint(f"Added Azure OpenAI service: {service_id}")
        
        # Register plugins with the kernel
        self._register_plugins()
        
        self._vprint(f"Kernel initialized with {len(self.kernel.plugins)} plugins")
        return self.kernel
    
    def _register_plugins(self):
        """Register all plugins with the kernel"""
        # Create plugin instances
        processor_plugin = QuestionnaireProcessorPlugin()
        blob_plugin = BlobPlugin()
        review_plugin = ReviewPlugin()
        
        # Add plugins to kernel
        self.kernel.add_plugin(
            processor_plugin,
            plugin_name="QuestionnaireProcessor",
            description="Handles Excel operations (load, persist)"
        )
        
        self.kernel.add_plugin(
            blob_plugin,
            plugin_name="BlobOperations", 
            description="Azure Blob Storage operations"
        )
        
        self.kernel.add_plugin(
            review_plugin,
            plugin_name="ReviewManager",
            description="Manages proposal review and approval"
        )
        
        self._vprint("Registered plugins: QuestionnaireProcessor, BlobOperations, ReviewManager")
    
    async def create_agent_with_kernel(self):
        """Create Azure AI Agent with Semantic Kernel and tools (Search + Function OpenAPI)"""
        if self.agent:
            return self.agent
        
        # Initialize kernel first
        await self.initialize_kernel()
        
        # Create agent client
        self._client_creds = AsyncDefaultAzureCredential()
        self._client_cm = AzureAIAgent.create_client(
            credential=self._client_creds,
            endpoint=self.endpoint
        )
        self.client = await self._client_cm.__aenter__()
        
        # Create a separate AIProjectClient for Agent B operations if needed
        if self.connected_agent_b_id:
            from azure.ai.projects.aio import AIProjectClient
            self.project_client = AIProjectClient(
                endpoint=self.endpoint,
                credential=self._client_creds
            )
            await self.project_client.__aenter__()
        else:
            self.project_client = None
        
        # Build tools
        tools = []
        tool_objects = []
        
        # Azure AI Search tool (knowledge) for Main Agent A (optional)
        try:
            if not self.disable_a_search_tool and self.search_connection_id:
                search_tool = AzureAISearchTool(
                    index_connection_id=self.search_connection_id,
                    index_name=self.search_index,
                    query_type=AzureAISearchQueryType.SIMPLE,
                    # Default filter by appId; agent may override
                    filter=f"appId eq '{self.app_id}'",
                    top_k=50,
                )
                tool_objects.append(search_tool)
                self._vprint("Added Azure AI Search tool to main agent")
            else:
                self._vprint("Main agent Search tool disabled (using connected agent B if configured)")
        except Exception as e:
            raise RuntimeError(f"Failed to configure Azure AI Search tool: {e}")
        
        # Connected Agent B (delegated retrieval)
        if self.connected_agent_b_id:
            try:
                connected_tool = ConnectedAgentTool(
                    id=self.connected_agent_b_id,
                    name=self.connected_agent_b_name,
                    description=self.connected_agent_b_desc,
                )
                tool_objects.append(connected_tool)
                self._vprint(f"Added Connected Agent tool: {self.connected_agent_b_name} -> {self.connected_agent_b_id}")
            except Exception as e:
                raise RuntimeError(f"Failed to configure Connected Agent tool: {e}")
        
        # OpenAPI tool for Function App (inline spec hosted in code)
        if self.func_base_url and self.func_api_key:
            try:
                base = self.func_base_url.rstrip('/')
                # Full endpoint with route and API key embedded in server URL
                full_endpoint = f"{base}/api/index?code={self.func_api_key}"
                openapi_doc = {
                    "openapi": "3.0.1",
                    "info": {"title": "Indexer Function", "version": "1.0.0"},
                    "servers": [{"url": full_endpoint}],
                    "paths": {
                        "/": {
                            "post": {
                                "operationId": "indexContainer",
                                "summary": "Index a container for a given appId",
                                "requestBody": {
                                    "required": True,
                                    "content": {
                                        "application/json": {
                                            "schema": {
                                                "type": "object",
                                                "properties": {
                                                    "appId": {"type": "string"},
                                                    "container": {"type": "string"},
                                                    "blobName": {"type": ["string", "null"]},
                                                },
                                                "required": ["appId", "container"],
                                            }
                                        }
                                    }
                                },
                                "responses": {
                                    "200": {
                                        "description": "OK",
                                        "content": {"application/json": {"schema": {"type": "object"}}}
                                    }
                                }
                            }
                        }
                    }
                }
                openapi_tool = OpenApiTool(
                    name="IndexerAPI",
                    description="HTTP trigger that indexes a container for a given appId.",
                    spec=openapi_doc,
                    auth=OpenApiAnonymousAuthDetails(),
                )
                tool_objects.append(openapi_tool)
                self._vprint("Added Function OpenAPI tool (inline spec)")
            except Exception as e:
                raise RuntimeError(f"Failed to configure Function OpenAPI tool: {e}")
        else:
            self._vprint("Function tool not configured (set FUNC_BASE_URL and FUNC_API_KEY to enable)")
        
        # Convert tool objects to definitions and aggregate resources
        for t in tool_objects:
            tools.extend(t.definitions)
        # Aggregate resources (only azure_ai_search currently contributes)
        resources_dict = {}
        for t in tool_objects:
            res = getattr(t, "resources", None)
            if not res:
                continue
            if hasattr(res, "azure_ai_search") and getattr(res, "azure_ai_search"):
                resources_dict["azure_ai_search"] = getattr(res, "azure_ai_search")
        tool_resources = ToolResources(**resources_dict) if resources_dict else None
        
        # Define agent instructions
        instructions = self._get_agent_instructions()
        
        # Create agent definition with tool definitions and resources
        agent_definition = await self.client.agents.create_agent(
            model=self.model_deployment,
            name=f"SK_Questionnaire_Agent_{self.app_id}",
            instructions=instructions,
            tools=tools,
            tool_resources=tool_resources,
            headers={"x-ms-enable-preview": "true"},
        )
        
        # Create agent with kernel plugins (function tools)
        self.agent = AzureAIAgent(
            client=self.client,
            definition=agent_definition,
            kernel=self.kernel  # Pass the kernel with registered plugins
        )
        
        self._vprint(f"Created agent {self.agent.id} with kernel plugins and tools")
        return self.agent
    
    def _get_agent_instructions(self) -> str:
        """Get agent instructions with generic examples"""
        connected_hint = (
            f"- Connected agent '{self.connected_agent_b_name}': Delegate retrieval for each question. "
            "Send only the minimal question text and filter. Expect compact JSON. Use this instead of direct search when available.\n"
            if self.connected_agent_b_id else ""
        )
        
        # Generic examples that guide without exposing real data
        generic_examples = """
EXAMPLE Q&A PATTERNS (generic):
1. Q: "What is the application name/title?" 
   → Search for: application name, app name, system name, product name
   
2. Q: "What compute/hosting services are used?"
   → Search for: compute, hosting, servers, infrastructure, Azure services
   
3. Q: "What database technology is used?"
   → Search for: database, DB, SQL, storage, data tier
   
4. Q: "What are the disaster recovery requirements?"
   → Search for: disaster recovery, DR, RPO, RTO, backup, failover
   
5. Q: "What security measures are in place?"
   → Search for: security, authentication, authorization, encryption, compliance

SEARCH STRATEGY:
- Extract key terms from the question
- Search for both exact matches and related terms
- If a question asks about "X", also search for common variations of X
- Return only what is found in documents, never generate answers
"""
        
        return f"""
You are a Semantic Kernel-powered Questionnaire Assessment Agent.

CRITICAL RULES:
1. You MUST retrieve answers ONLY from the Azure AI Search index
2. NEVER generate, infer, or make up answers based on general knowledge
3. If no answer is found in search results, leave the field blank
4. Always use the search tool or connected agent for EVERY question

{generic_examples}

TOOLS:
- Azure AI Search (knowledge): Search index '{self.search_index}' with filter: appId eq '{self.app_id}'
{connected_hint}- OpenAPI Function (indexContainer): Index container for the application
- Function tools (Kernel):
  - BlobOperations: download/upload/list blobs
  - QuestionnaireProcessor: initialize_questionnaire, persist_answers, get_excel_path
  - ReviewManager: add_proposals, render_markdown, get_updates_json, clear

WORKFLOW:
PHASE 0: Setup
- Ask for container name and workbook blob name
- List sheets and ask user which to use

PHASE 1: Index content
- Call indexContainer with appId and container
- Ensure documents are indexed (uploaded >= 1)

PHASE 2: Initialize
- Download workbook and initialize with chosen sheets

PHASE 3: Search and Extract
- For EACH question: search the index for the answer
- Use relevant keywords from the question
- Try multiple search queries if needed
- Only use information found in search results
- Mark as "Not found in documents" if no answer exists

PHASE 4: Review
- Show results table for user review

PHASE 5: Save
- Persist approved answers and upload

IMPORTANT:
- Every answer must come from search results only
- Do not use your training knowledge to answer questions
- If unsure, leave blank rather than guess
"""

    async def chat_with_kernel(self, user_inputs: List[str]) -> None:
        """Chat using the kernel-based agent"""
        await self.create_agent_with_kernel()
        thread: AzureAIAgentThread = None
        
        try:
            for user_input in user_inputs:
                # Invoke agent with kernel context
                async for response in self.agent.invoke(
                    messages=user_input,
                    thread=thread,
                    kernel=self.kernel  # Pass kernel for function execution
                ):
                    print(response)
                    thread = response.thread
                    
        finally:
            await self._cleanup(thread)
    
    async def delegate_search_to_agent_b(self, question: str, row_index: int, sheet_name: str) -> dict:
        """Delegate a single question search to Agent B with minimal context"""
        if not self.connected_agent_b_id:
            raise RuntimeError("Connected Agent B not configured")
        
        if not self.project_client:
            raise RuntimeError("Project client not initialized")
        
        # Create a minimal thread just for this question
        thread = None
        try:
            # Create a thread
            thread = await self.project_client.agents.threads.create()
            
            # Very explicit prompt to prevent hallucination
            search_prompt = f"""IMPORTANT: You MUST use Azure AI Search to find the answer. DO NOT generate or make up answers.

Use the {self.connected_agent_b_name} tool to search for:
Question: {question}
Filter: appId eq '{self.app_id}'

INSTRUCTIONS FOR SEARCH:
1. Search the Azure AI Search index for relevant documents
2. Extract the answer ONLY from search results
3. If no results found, return empty Answer
4. DO NOT generate answers from your knowledge
5. Return ONLY this JSON format:
{{"Answer":"<text from search results only>","Confidence":"<High if exact match, Medium if partial, Low if uncertain>","Source":"<document name from search>"}}

If search returns no results, return:
{{"Answer":"","Confidence":"Low","Source":"no-results"}}"""
            
            # Add message to thread
            await self.project_client.agents.messages.create(
                thread_id=thread.id,
                role="user",
                content=search_prompt
            )
            
            # Create and process run with strict instructions
            run = await self.project_client.agents.runs.create_and_process(
                thread_id=thread.id,
                agent_id=self.agent.id,
                instructions=f"""You are a search relay agent. Your ONLY job is to:
1. Use the {self.connected_agent_b_name} tool to search Azure AI Search
2. Return results EXACTLY as found in the search index
3. NEVER generate, infer, or make up answers
4. If search returns nothing, say so clearly
5. Return JSON format only

DO NOT use your training data to answer questions. ONLY use search results.""",
                temperature=0.0,  # Set to 0 for deterministic behavior
                max_completion_tokens=500  # Limit response size
            )
            
            # Check run status
            if run.status == "failed":
                self._vprint(f"Run failed: {run.last_error}")
                return {
                    "RowIndex": row_index,
                    "SheetName": sheet_name,
                    "Question": question,
                    "Answer": "",
                    "Confidence": "Low",
                    "Provenance": "run-failed"
                }
            
            # Extract result from messages
            if run.status == "completed":
                messages = self.project_client.agents.messages.list(
                    thread_id=thread.id,
                    order="desc"
                )
                
                async for message in messages:
                    if message.role == "assistant":
                        content_text = ""
                        if hasattr(message, 'content'):
                            if isinstance(message.content, str):
                                content_text = message.content
                            elif isinstance(message.content, list):
                                for content in message.content:
                                    if hasattr(content, 'text'):
                                        if hasattr(content.text, 'value'):
                                            content_text = content.text.value
                                        else:
                                            content_text = str(content.text)
                                        break
                        
                        if content_text:
                            try:
                                # Extract JSON from response
                                import re
                                json_match = re.search(r'\{[^}]+\}', content_text)
                                if json_match:
                                    result = json.loads(json_match.group())
                                else:
                                    result = json.loads(content_text)
                                
                                # Validate that answer isn't hallucinated
                                answer = result.get("Answer", "")
                                source = result.get("Source", "")
                                
                                # If source is missing or generic, likely hallucinated
                                if answer and source in ["", "no-results", "unknown", None]:
                                    self._vprint(f"Warning: Possible hallucination detected for question {row_index}")
                                    answer = ""  # Clear potentially hallucinated answer
                                
                                return {
                                    "RowIndex": row_index,
                                    "SheetName": sheet_name,
                                    "Question": question,
                                    "Answer": answer,
                                    "Confidence": result.get("Confidence", "Low"),
                                    "Provenance": source or "no-source"
                                }
                            except Exception as e:
                                self._vprint(f"Failed to parse JSON: {e}")
                        break
            
            # Default if failed
            return {
                "RowIndex": row_index,
                "SheetName": sheet_name,
                "Question": question,
                "Answer": "",
                "Confidence": "Low",
                "Provenance": "search-failed"
            }
                
        except Exception as e:
            self._vprint(f"Error in delegate_search_to_agent_b: {e}")
            return {
                "RowIndex": row_index,
                "SheetName": sheet_name,
                "Question": question,
                "Answer": "",
                "Confidence": "Low",
                "Provenance": f"error: {str(e)[:50]}"
            }
        finally:
            if thread:
                try:
                    await self.project_client.agents.threads.delete(thread.id)
                except:
                    pass

    async def batch_search_questions(self, questions: List[dict], batch_size: int = 5) -> List[dict]:
        """Process questions in batches through Agent B"""
        print(f"\n=== Starting Batch Search for {len(questions)} questions ===")
        proposals = []
        
        # Process in batches with concurrency control
        semaphore = asyncio.Semaphore(3)  # Max 3 concurrent searches
        
        async def search_with_limit(q):
            async with semaphore:
                try:
                    return await self.delegate_search_to_agent_b(
                        q.get("Question", ""),
                        q.get("RowIndex", 0),
                        q.get("SheetName", "Sheet1")
                    )
                except Exception as e:
                    self._vprint(f"Search failed for question: {e}")
                    return {
                        "RowIndex": q.get("RowIndex", 0),
                        "SheetName": q.get("SheetName", "Sheet1"),
                        "Question": q.get("Question", ""),
                        "Answer": "",
                        "Confidence": "Low",
                        "Provenance": "error"
                    }
        
        # Process in batches to show progress
        for i in range(0, len(questions), batch_size):
            batch_end = min(i + batch_size, len(questions))
            batch = questions[i:batch_end]
            
            print(f"  Processing questions {i+1} to {batch_end}...")
            
            # Create tasks for this batch
            tasks = [search_with_limit(q) for q in batch]
            
            # Execute batch
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            batch_proposals = []
            for result in results:
                if isinstance(result, dict):
                    batch_proposals.append(result)
                    proposals.append(result)
            
            # Add batch to review manager
            if batch_proposals:
                proposals_json = json.dumps({"proposals": batch_proposals})
                await self.kernel.invoke(
                    function_name="add_proposals",
                    plugin_name="ReviewManager",
                    proposals_json=proposals_json
                )
            
            # Small delay between batches
            await asyncio.sleep(2)
            
            print(f"    ✓ Completed {len(proposals)}/{len(questions)} questions")
        
        print(f"\n=== Search Complete: {len(proposals)} answers found ===\n")
        return proposals
    
    async def chat_repl_with_kernel(self, initial_prompt: str) -> None:
        """Interactive REPL chat with automatic batch search when questions are loaded"""
        await self.create_agent_with_kernel()
        thread: AzureAIAgentThread = None
        questions_loaded = False
        search_completed = False
        
        async def invoke_with_retry(message: str, thread_obj: Optional[AzureAIAgentThread]):
            """Invoke with retry logic for rate limits"""
            backoff = 5
            while True:
                try:
                    async for response in self.agent.invoke(
                        messages=message,
                        thread=thread_obj,
                        kernel=self.kernel
                    ):
                        print(response)
                        return response.thread
                except Exception as e:
                    msg = str(e)
                    m = re.search(r"Try again in\s*([0-9]+)\s*seconds", msg, re.IGNORECASE)
                    wait = int(m.group(1)) if m else backoff
                    self._vprint(f"Rate limit hit. Waiting {wait}s...")
                    await asyncio.sleep(wait)
                    backoff = min(backoff * 2, 30)
        
        async def check_and_process_questions():
            """Check if questions are loaded and process them through Agent B"""
            nonlocal questions_loaded, search_completed
            
            if questions_loaded or search_completed:
                return False
            
            try:
                # Check if questions are loaded
                questions_json = await self.kernel.invoke(
                    function_name="get_loaded_questions",
                    plugin_name="QuestionnaireProcessor"
                )
                questions = json.loads(str(questions_json)) if questions_json else []
                
                if questions and len(questions) > 0:
                    questions_loaded = True
                    print(f"\n🔍 Detected {len(questions)} loaded questions. Starting automatic search through Agent B...")
                    
                    # Perform batch search
                    if self.connected_agent_b_id:
                        await self.batch_search_questions(questions, batch_size=5)
                        search_completed = True
                        
                        # Show review table
                        markdown = await self.kernel.invoke(
                            function_name="render_markdown",
                            plugin_name="ReviewManager"
                        )
                        print("\n📊 Search Results:")
                        print(str(markdown))
                        
                        return True
                    else:
                        print("⚠️ Agent B not configured. Please set CONNECTED_AGENT_B_ID environment variable.")
                        return False
                        
            except Exception as e:
                # Questions not yet loaded, continue normally
                return False
            
            return False
        
        try:
            # Send initial prompt
            thread = await invoke_with_retry(initial_prompt, thread)
            
            # Interactive loop
            while True:
                # Check if we should auto-process questions
                if await check_and_process_questions():
                    print("\n✅ Automatic search completed. You can now:")
                    print("1. Review and edit answers")
                    print("2. Save the completed questionnaire")
                    print("3. Type 'save' to persist and upload")
                    print("4. Type 'exit' to quit")
                
                try:
                    user_input = await asyncio.get_event_loop().run_in_executor(
                        None, 
                        lambda: input("You: ").strip()
                    )
                except Exception:
                    break
                    
                if not user_input or user_input.lower() in ("exit", "quit"):
                    break
                
                # Handle save command
                if user_input.lower() == "save" and search_completed:
                    # Prefer direct kernel path to avoid large tool payloads and rate limits
                    await self.save_with_kernel()
                    continue
                else:
                    thread = await invoke_with_retry(user_input, thread)
                
        finally:
            await self._cleanup(thread)
    
    async def save_with_kernel(self, container_default: Optional[str] = None):
        try:
            # 1) Get updates (local, no LLM) - extract the value properly
            updates_result = await self.kernel.invoke(
                function_name="get_updates_json",
                plugin_name="ReviewManager"
            )
            # Extract the actual value from the FunctionResult
            updates_json = updates_result.value if hasattr(updates_result, 'value') else str(updates_result)
            
            # Debug: Check what we got
            print(f"DEBUG: Got updates type: {type(updates_json)}, length: {len(updates_json) if isinstance(updates_json, str) else 'N/A'}")
            
            # Parse to verify we have actual data
            try:
                updates_list = json.loads(updates_json) if isinstance(updates_json, str) else updates_json
                print(f"Updates to persist: {len(updates_list)} answers")
                if len(updates_list) == 0:
                    print("WARNING: No updates to save! Check if proposals were added correctly.")
                    return
            except Exception as e:
                print(f"ERROR parsing updates: {e}")
                print(f"Raw updates_json: {updates_json[:500] if isinstance(updates_json, str) else updates_json}")
                return

            # 2) Persist to Excel (local, no LLM) - pass the actual JSON string
            persist_result = await self.kernel.invoke(
                function_name="persist_answers",
                plugin_name="QuestionnaireProcessor",
                updates_json=updates_json  # Pass the actual JSON string, not str() of the result object
            )
            persist_status = persist_result.value if hasattr(persist_result, 'value') else str(persist_result)
            print(f"Persist status: {persist_status}")

            # 3) Get path and upload
            path_result = await self.kernel.invoke(
                function_name="get_excel_path",
                plugin_name="QuestionnaireProcessor"
            )
            local_path = path_result.value if hasattr(path_result, 'value') else str(path_result)
            
            if not local_path or local_path == "":
                print("ERROR: No Excel path available. Excel may not be initialized.")
                return
                
            print(f"Excel path: {local_path}")
            
            # Check if file exists and has been modified
            if os.path.exists(local_path):
                file_size = os.path.getsize(local_path)
                print(f"File exists at {local_path}, size: {file_size} bytes")
            else:
                print(f"WARNING: File not found at {local_path}")
                return
            
            base = os.path.splitext(os.path.basename(local_path))[0]
            dest_name = f"{base}_filled.xlsx"

            container = container_default or input("Container to upload to: ").strip()
            
            upload_result = await self.kernel.invoke(
                function_name="upload_file",
                plugin_name="BlobOperations",
                container=container,
                local_path=local_path,
                dest_blob_name=dest_name
            )
            upload_url = upload_result.value if hasattr(upload_result, 'value') else str(upload_result)
            print(f"Saved and uploaded: {upload_url}")
            
        except Exception as e:
            print(f"ERROR in save_with_kernel: {e}")
            import traceback
            traceback.print_exc()

    async def _cleanup(self, thread: Optional[AzureAIAgentThread]):
        """Clean up resources"""
        try:
            if thread:
                await thread.delete()
        except Exception:
            pass
            
        try:
            if self.agent and self.client:
                agent_id = getattr(self.agent, 'id', None)
                if agent_id:
                    await self.client.agents.delete_agent(agent_id)
        except Exception:
            pass
        
        try:
            if hasattr(self, "project_client") and self.project_client:
                await self.project_client.__aexit__(None, None, None)
        except Exception:
            pass
            
        try:
            if hasattr(self, "_client_cm") and self._client_cm:
                await self._client_cm.__aexit__(None, None, None)
        except Exception:
            pass
            
        try:
            if hasattr(self, "_client_creds") and self._client_creds:
                await self._client_creds.close()
        except Exception:
            pass
    
    async def close(self):
        """Close all resources"""
        await self._cleanup(None)


# Direct kernel execution (without agent)
async def execute_with_kernel_directly(app_id: str):
    """Example of direct kernel execution without agent"""
    kernel = Kernel()
    
    # Register plugins
    kernel.add_plugin(QuestionnaireProcessorPlugin(), "QuestionnaireProcessor")
    kernel.add_plugin(BlobPlugin(), "BlobOperations")
    kernel.add_plugin(ReviewPlugin(), "ReviewManager")
    
    # Example: list blobs only (avoid search functions here)
    _ = await kernel.invoke_function_call(
        plugin_name="BlobOperations",
        function_name="list_blobs",
        container="myapp01"
    )
    return kernel