import os
import sys
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import MessageRole, ListSortOrder

def start_orchestrator_conversation(orchestrator_id=None):
    load_dotenv()
    PROJECT_ENDPOINT = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
    
    if not orchestrator_id:
        orchestrator_id = os.getenv("ORCHESTRATOR_AGENT_ID")
    
    if not orchestrator_id:
        print("Please provide an orchestrator agent ID or set ORCHESTRATOR_AGENT_ID in .env")
        return

    # Initialize the AIProjectClient
    project_client = AIProjectClient(
        endpoint=PROJECT_ENDPOINT,
        credential=DefaultAzureCredential(exclude_interactive_browser_credential=False)
    )

    # Get the orchestrator agent
    orchestrator = project_client.agents.get_agent(orchestrator_id)
    print(f"\n🤖 SBD-Orchestrator Ready!")
    print(f"Agent: {orchestrator.name} (ID: {orchestrator.id})")
    print("\nProvide URLs for analysis:")
    print("- Azure DevOps wiki URLs → Architecture Agent")
    print("- GitHub URLs → Code Analyzer Agent")
    print("\nYou can provide one or both types of URLs.\n")

    # Create a new thread for the conversation
    thread = project_client.agents.threads.create()

    # Main conversation loop
    while True:
        user_input = input("\nEnter URL(s) or 'quit' to exit: ").strip()
        
        if user_input.lower() == 'quit':
            break
            
        if not user_input:
            print("Please enter at least one URL.")
            continue

        # Send the message to orchestrator
        message = project_client.agents.messages.create(
            thread_id=thread.id,
            role=MessageRole.USER,
            content=user_input
        )

        print("\n⏳ Processing your request...")
        
        # Process the run
        run = project_client.agents.runs.create_and_process(
            thread_id=thread.id,
            agent_id=orchestrator.id
        )

        if run.status == "failed":
            print(f"\n❌ Run failed: {run.last_error}")
        else:
            # Get the orchestrator's response
            last_msg = project_client.agents.messages.get_last_message_text_by_role(
                thread_id=thread.id,
                role=MessageRole.AGENT,
            )
            if last_msg:
                print(f"\n📊 Analysis Results:")
                print("-" * 80)
                print(last_msg.text.value)
                print("-" * 80)

    # Show conversation history
    print("\n\n📝 Conversation History:")
    print("=" * 80)
    messages = project_client.agents.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
    for message in messages:
        if message.text_messages:
            last_msg = message.text_messages[-1]
            print(f"\n{message.role.upper()}:")
            print(last_msg.text.value)
            print("-" * 40)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        start_orchestrator_conversation(orchestrator_id=sys.argv[1])
    else:
        start_orchestrator_conversation()