import os
import sys
import asyncio
import argparse
from dotenv import load_dotenv
from agent_sk import QuestionnaireAgentSK
load_dotenv()

async def run_orchestrated_sk(app_id: str, prompt: str):
    """Run the Semantic Kernel-based agent"""
    agent = QuestionnaireAgentSK(app_id)
    
    try:
        # Interactive mode
        await agent.chat_repl_with_kernel(prompt)
    finally:
        await agent.close()

def main():
    parser = argparse.ArgumentParser(description="Questionnaire Agent with Semantic Kernel")
    parser.add_argument("--orchestrate", action="store_true", 
                       help="Run SK agent orchestration flow")
    parser.add_argument("--prompt", 
                       default="Start the questionnaire orchestration.",
                       help="Initial instruction to the agent")
    parser.add_argument("--app-id", required=True,
                       help="Application ID for the assessment (also used as container name)")
    
    args = parser.parse_args()
    
    if args.orchestrate:
        asyncio.run(run_orchestrated_sk(args.app_id, args.prompt))
    else:
        print("Please specify --orchestrate")
        sys.exit(1)


if __name__ == "__main__":
    main()