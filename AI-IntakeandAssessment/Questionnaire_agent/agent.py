import os
import asyncio
import re
import random
from typing import Callable, Optional, Dict, List, Tuple
from datetime import datetime, timezone
from azure.identity import DefaultAzureCredential
from azure.identity import AzureCliCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import ConnectionType
from azure.ai.agents.models import AzureAISearchTool, AzureAISearchQueryType
from azure.identity.aio import DefaultAzureCredential as AsyncDefaultAzureCredential
from semantic_kernel.agents import AzureAIAgent, AzureAIAgentSettings, AzureAIAgentThread
from semantic_kernel.contents import ChatMessageContent, FunctionCallContent, FunctionResultContent

from tools.excel import load_questions, update_answers, ensure_columns, _parse_sheet_names
from tools.confidence import score_confidence
from tools.telemetry import TelemetryLogger

class QuestionnaireAgent:
    def __init__(self, app_id: str):
        self.app_id = app_id
        self.verbose = os.getenv("ASSESS_DEBUG", "0") in ("1", "true", "True", "yes")
        self.telemetry = TelemetryLogger()
        
        # Validate environment
        endpoint = os.getenv("AZURE_AI_AGENT_ENDPOINT")
        model_deployment = os.getenv("AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME")
        search_index = os.getenv("AZURE_SEARCH_INDEX")
        search_connection = os.getenv("AZURE_SEARCH_CONNECTION_NAME")  # Add optional connection name
        
        # Get target sheets from environment
        self.target_sheets = _parse_sheet_names(os.getenv("EXCEL_SHEETS"))
        
        missing = []
        if not endpoint:
            missing.append("AZURE_AI_AGENT_ENDPOINT")
        if not model_deployment:
            missing.append("AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME")
        if not search_index:
            missing.append("AZURE_SEARCH_INDEX")
            
        if missing:
            raise RuntimeError(f"Missing required env vars: {', '.join(missing)}")
        
        self.endpoint = endpoint
        self.model_deployment = model_deployment
        self.search_index = search_index
        self.search_connection_name = search_connection  # Optional: specify which connection to use
        self.agent = None
        self.client = None
        self.thread_id = None  # Store thread ID for reference

    def _vprint(self, msg: str):
        if self.verbose:
            print(msg)

    async def _create_agent(self):
        """Create the Azure AI Agent with search tool attached."""
        if self.agent:
            return
            
        # Use synchronous credential for AIProjectClient
        sync_credential = AzureCliCredential()
        async_credential = AsyncDefaultAzureCredential()
        
        # Create synchronous project client for connections
        project_client = AIProjectClient(
            endpoint=self.endpoint,
            credential=sync_credential
        )
        
        # Get Azure AI Search connection
        try:
            azure_ai_conn_id = None
            
            if self.search_connection_name:
                # If connection name is specified, try to get it directly
                try:
                    conn = project_client.connections.get(self.search_connection_name)
                    azure_ai_conn_id = conn.id
                    self._vprint(f"Using specified Azure AI Search connection: {conn.name}")
                except Exception:
                    self._vprint(f"Specified connection '{self.search_connection_name}' not found, searching for any Azure AI Search connection")
            
            if not azure_ai_conn_id:
                # List all connections to find the right one
                connections = project_client.connections.list()
                search_connections = []
                
                for conn in connections:
                    # Check the connection type - it might be stored differently
                    conn_type = getattr(conn, 'connection_type', None) or getattr(conn, 'type', None)
                    if conn_type == ConnectionType.AZURE_AI_SEARCH:
                        search_connections.append(conn)
                        self._vprint(f"Found Azure AI Search connection: {conn.name}")

                # Select the connection that matches the search index endpoint if possible
                # Otherwise use the first available
                if search_connections:
                    azure_ai_conn_id = search_connections[0].id
                    if len(search_connections) > 1:
                        self._vprint(f"Multiple Azure AI Search connections found. Using: {search_connections[0].name}")
                        self._vprint("Set AZURE_SEARCH_CONNECTION_NAME env var to specify which one to use")
                
            if not azure_ai_conn_id:
                # If no connection found, try get_default
                azure_ai_conn_id = project_client.connections.get_default(ConnectionType.AZURE_AI_SEARCH).id
                
            self._vprint(f"Using Azure AI Search connection:")
            self._vprint(f"Using search index: {self.search_index}")
        except Exception as e:
            raise RuntimeError(f"Failed to get Azure AI Search connection: {e}")
        
        # Configure search tool
        search_tool = AzureAISearchTool(
            index_connection_id=azure_ai_conn_id,
            index_name=self.search_index,
            query_type=AzureAISearchQueryType.SEMANTIC,
            top_k=20  # Retrieve more candidates for better coverage
        )
        
        # Agent instructions specifically for questionnaire processing
        instructions = f"""You are a migration assessment assistant analyzing documents for application '{self.app_id}'.

Your task is to answer questions about the application by searching through indexed documents.

Rules:
1. Use ONLY information from the search results to answer questions
2. Search for relevant information using the Azure AI Search tool
3. If guidance is provided with a question, use it to better understand what information to look for
4. If the answer is found in search results, provide a concise response
5. If no relevant information is found, respond with exactly: "NOT_FOUND"
6. For technical questions (databases, services, security), extract specific technology names
7. Normalize technology names appropriately (e.g., "Azure SQL Database" can be "SQL" or "Azure SQL")
8. For lists, provide comma-separated values (maximum 3 items)
9. Keep answers brief - single phrases or short lists only

Search Strategy:
- Always filter searches by appId='{self.app_id}'
- When guidance is provided, use keywords from the guidance in your search
- Try different query phrasings if initial search doesn't yield results
- Look for both explicit mentions and contextual clues

Examples:
- Question: "What is the application name?" → Answer: "DemoApp"
- Question: "What database is used?" → Answer: "Azure SQL Database" or "SQL"
- Question: "What are the security requirements?" → Answer: "WAF, Private Endpoints, TLS 1.2"
- Question: "What is the favorite color?" → Answer: "NOT_FOUND"
"""

        # Create client synchronously (it's not async)
        self.client = AzureAIAgent.create_client(
            credential=async_credential,
            endpoint=self.endpoint
        )
        
        # Create agent definition - this is async
        agent_definition = await self.client.agents.create_agent(
            model=self.model_deployment,
            name=f"QuestionnaireAgent_{self.app_id}",
            instructions=instructions,
            tools=search_tool.definitions,
            tool_resources=search_tool.resources,
            headers={"x-ms-enable-preview": "true"}
        )
        
        # Create Semantic Kernel agent
        self.agent = AzureAIAgent(
            client=self.client,
            definition=agent_definition
        )
        
        self._vprint(f"Created agent: {agent_definition.id}")
        print(f"\n✅ Agent created successfully!")
        print(f"   Agent ID: {agent_definition.id}")
        print(f"   Agent Name: QuestionnaireAgent_{self.app_id}")

    async def _get_answer(self, question: str, guidance: Optional[str], thread: Optional[AzureAIAgentThread]) -> Tuple[str, Optional[AzureAIAgentThread], List[str]]:
        """Get answer from agent with search tool, applying retry/backoff on rate limits."""
        if not thread:
            # Create thread with the client
            thread = AzureAIAgentThread(client=self.client)
            if hasattr(thread, 'id'):
                self.thread_id = thread.id
                self._vprint(f"Created new thread: {thread.id}")
        
        search_queries = []
        if guidance:
            full_question = f"{question}\n\nGuidance: {guidance}"
            self._vprint(f"Question with guidance: {full_question}")
        else:
            full_question = question

        async def capture_search_calls(message: ChatMessageContent):
            for item in message.items or []:
                if isinstance(item, FunctionCallContent) and "search" in item.name.lower():
                    args = item.arguments if isinstance(item.arguments, dict) else {}
                    query = args.get("query", "")
                    if query:
                        search_queries.append(query)
                        self._vprint(f"Agent searching for: {query}")

        # Retry loop with exponential backoff + jitter for rate limits
        max_retries = 5
        backoff = 1.0
        response = None
        for attempt in range(1, max_retries + 1):
            try:
                response = await self.agent.get_response(
                    messages=full_question,
                    thread=thread,
                    on_intermediate_message=capture_search_calls
                )
                break
            except Exception as e:
                msg = str(e) or ""
                # Detect rate-limit message and extract suggested wait if present
                if "rate limit" in msg.lower() or "try again" in msg.lower():
                    m = re.search(r"Try again in\s*([0-9]+)\s*seconds", msg, re.IGNORECASE)
                    wait = int(m.group(1)) if m else int(backoff)
                    jitter = random.uniform(0, 0.5)
                    wait_time = max(0.5, wait) + jitter
                    self._vprint(f"Rate limit detected (attempt {attempt}/{max_retries}). Sleeping {wait_time:.2f}s before retry.")
                    await asyncio.sleep(wait_time)
                    backoff = min(backoff * 2, 30)
                    continue
                # Non-rate errors: re-raise after logging
                self._vprint(f"Agent.get_response failed: {msg}")
                raise

        if response is None:
            # All retries exhausted
            raise RuntimeError("Agent invocation failed after retries due to rate limits or errors.")

        answer_text = str(response).strip()

        if answer_text.upper() == "NOT_FOUND":
            return None, response.thread, search_queries

        return answer_text, response.thread, search_queries

    async def close(self) -> None:
        """Close underlying client sessions (call on shutdown)."""
        try:
            if self.client and hasattr(self.client, "close"):
                maybe = self.client.close()
                if asyncio.iscoroutine(maybe):
                    await maybe
        except Exception:
            pass

    def run(self, excel_path: str, user_ask_fn: Callable[[str], str]) -> None:
        """Run the questionnaire processing asynchronously."""
        asyncio.run(self._run_async(excel_path, user_ask_fn))

    async def _run_async(self, excel_path: str, user_ask_fn: Callable[[str], str]) -> None:
        # Print sheet configuration
        if self.target_sheets:
            print(f"\n📋 Processing specific sheets: {', '.join(self.target_sheets)}")
        else:
            print(f"\n📋 Processing active sheet only (no specific sheets configured)")
            print(f"   To process specific sheets, set EXCEL_SHEETS in your .env file")
            print(f"   Example: EXCEL_SHEETS=Sheet1,Sheet2,Data")
        
        # Ensure columns and get column mappings
        sheet_column_maps = ensure_columns(excel_path, self.target_sheets)
        rows, sheet_column_maps = load_questions(excel_path, self.target_sheets)
        
        updates = []
        run_id = f"{self.app_id}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
        
        # Log column information per sheet
        for sheet_name, column_map in sheet_column_maps.items():
            self._vprint(f"\nSheet '{sheet_name}' column mappings: {column_map}")
            if column_map.get("guidance"):
                print(f"✅ Sheet '{sheet_name}': Found guidance column '{column_map['guidance']}'")
            else:
                print(f"ℹ️  Sheet '{sheet_name}': No guidance column found")
            print(f"✅ Sheet '{sheet_name}': Using answer column '{column_map['answer']}'")
        
        # Create agent
        await self._create_agent()
        
        # Process questions with a single thread for conversation continuity
        thread = None
        
        for r in rows:
            row_idx = r["RowIndex"]
            sheet_name = r["SheetName"]
            question = r["Question"]
            guidance = r.get("Guidance", None)
            
            self._vprint(f"\n[Sheet:{sheet_name}, Row:{row_idx}] Processing: {question}")
            if guidance:
                self._vprint(f"[Sheet:{sheet_name}, Row:{row_idx}] With guidance: {guidance}")
            
            # Get answer from agent
            answer, thread, search_queries = await self._get_answer(question, guidance, thread)
            
            # Determine provenance
            if answer:
                provenance = f"ai-search:{self.search_index}"
                confidence = "High"  # Agent found answer in index
                self._vprint(f"[Sheet:{sheet_name}, Row:{row_idx}] Agent found answer: {answer[:100]}")
            else:
                # No answer found - ask user
                self._vprint(f"[Sheet:{sheet_name}, Row:{row_idx}] No answer found in index; prompting user.")
                self._vprint(f"[Sheet:{sheet_name}, Row:{row_idx}] Agent tried these searches: {search_queries}")
                
                # Include guidance and sheet info in user prompt
                prompt_parts = [f"[From sheet: {sheet_name}]", question]
                if guidance:
                    prompt_parts.append(f"(Guidance: {guidance})")
                prompt = "\n".join(prompt_parts)
                    
                user_answer = user_ask_fn(prompt).strip()
                if user_answer:
                    answer = user_answer
                    provenance = "user:interactive"
                    confidence = "High"  # User provided
                else:
                    answer = "Unknown"
                    provenance = "none"
                    confidence = "Unknown"
            
            # Record update with sheet information
            updates.append({
                "RowIndex": row_idx,
                "SheetName": sheet_name,  # Include sheet name for proper routing
                "Answer": answer,
                "Confidence": confidence,
                "Provenance": provenance,
            })
            
            self._vprint(f"[Sheet:{sheet_name}, Row:{row_idx}] Writing: Answer='{answer[:60]}', "
                       f"Confidence='{confidence}', Provenance='{provenance}'")
            
            # Log telemetry
            try:
                self.telemetry.log_question_result(
                    app_id=self.app_id,
                    run_id=run_id,
                    question_id=f"{sheet_name}:{row_idx}",  # Include sheet in ID
                    question_text=question,
                    answer=answer or "",
                    confidence=confidence,
                    provenance=provenance,
                    retrieval_hits=search_queries
                )
            except Exception:
                pass
        
        # Write all updates to Excel with column mappings
        update_answers(excel_path, updates, sheet_column_maps, self.target_sheets)
        self._vprint("All updates written to Excel.")
        
        # Close agent client sessions to avoid "Unclosed client session" warnings
        try:
            await self.close()
        except Exception:
            pass
        
        # Print completion summary with preserved resources
        print(f"\n✅ Processing completed successfully!")
        print(f"   Processed {len(rows)} questions from {len(sheet_column_maps)} sheet(s)")
        print(f"   Agent ID: {self.agent.id if hasattr(self.agent, 'id') else 'N/A'}")
        if self.thread_id:
            print(f"   Thread ID: {self.thread_id}")
        print(f"\n💡 Note: Agent and thread have been preserved and can be reused.")
        print(f"   To continue the conversation, use the same agent and thread IDs.")