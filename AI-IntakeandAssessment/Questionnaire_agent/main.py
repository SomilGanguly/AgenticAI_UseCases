import os
import sys
import asyncio
import argparse
from dotenv import load_dotenv

load_dotenv()

from agent_sk import QuestionnaireAgentSK, execute_with_kernel_directly
from orchestrator_sk import SimpleQuestionnaireOrchestrator


async def run_orchestrated_sk(app_id: str, prompt: str):
    """Run the Semantic Kernel-based orchestrated agent"""
    agent = QuestionnaireAgentSK(app_id)
    
    try:
        # Interactive mode
        await agent.chat_repl_with_kernel(prompt)
    finally:
        await agent.close()


async def run_direct_kernel(app_id: str):
    """Run direct kernel execution without agent"""
    print("Running direct kernel execution...")
    await execute_with_kernel_directly(app_id)


async def run_simple_orchestrator(app_id: str, container: str, workbook: str):
    """Run simple orchestrator without agent complexity"""
    orchestrator = SimpleQuestionnaireOrchestrator(app_id)
    await orchestrator.initialize()
    await orchestrator.run_workflow(container, workbook)


def main():
    parser = argparse.ArgumentParser(description="Questionnaire Agent with Semantic Kernel")
    parser.add_argument("--orchestrate", action="store_true", 
                       help="Run SK agent orchestration flow")
    parser.add_argument("--direct", action="store_true",
                       help="Run direct kernel execution without agent")
    parser.add_argument("--simple", action="store_true",
                       help="Run simple orchestrator (recommended)")
    parser.add_argument("--prompt", 
                       default="Start the questionnaire orchestration.",
                       help="Initial instruction to the agent")
    parser.add_argument("--app-id", required=True,
                       help="Application ID for the assessment")
    parser.add_argument("--container", 
                       default="myapp01",
                       help="Azure Storage container name")
    parser.add_argument("--workbook",
                       default="ApplicationQuestionnaireV1.1.xlsx", 
                       help="Excel workbook name")
    
    args = parser.parse_args()
    
    if args.simple:
        asyncio.run(run_simple_orchestrator(args.app_id, args.container, args.workbook))
    elif args.direct:
        asyncio.run(run_direct_kernel(args.app_id))
    elif args.orchestrate:
        asyncio.run(run_orchestrated_sk(args.app_id, args.prompt))
    else:
        print("Please specify --orchestrate, --direct, or --simple")
        sys.exit(1)


if __name__ == "__main__":
    main()