from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import ListSortOrder

def analyze_with_foundry_agent(text, image_descriptions, foundry_endpoint, foundry_agent_id):
    """
    Send text and image analysis to Azure Foundry agent and return the agent's response.
    """
    project = AIProjectClient(
        credential=DefaultAzureCredential(),
        endpoint=foundry_endpoint
    )
    agent = project.agents.get_agent(foundry_agent_id)
    thread = project.agents.threads.create()
    print(f"[DEBUG] Created thread, ID: {thread.id}")

    # Compose message with text and image analysis
    content = (
        "Analyze the following architecture wiki page and image analysis results. "
        "Compare with the standard data in the connected search index. "
        "Return a structured list of non-compliant or mismatched values.\n\n"
        f"Wiki Text:\n{text}\n\nImage Analysis:\n{image_descriptions}"
    )
    project.agents.messages.create(
        thread_id=thread.id,
        role="user",
        content=content
    )
    run = project.agents.runs.create_and_process(
        thread_id=thread.id,
        agent_id=agent.id
    )
    if run.status == "failed":
        print(f"[ERROR] Run failed: {run.last_error}")
        return None
    messages = project.agents.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
    # Get the last assistant message
    for message in reversed(list(messages)):
        if message.role == "assistant" and message.text_messages:
            return message.text_messages[-1].text.value
    return None
