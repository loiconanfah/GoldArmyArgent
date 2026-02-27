
import asyncio
import os
import sys
import traceback
from agents.headhunter import headhunter_agent

async def run_diagnostic():
    print("Initializing...")
    await headhunter_agent.initialize()
    print("Agent Initialized. Running find_decision_makers for Microsoft...")
    
    try:
        profiles = await headhunter_agent.find_decision_makers({"company_name": "Microsoft"})
        print(f"Returned {len(profiles)} profiles.")
        for p in profiles:
            print(p)
    except Exception as e:
        print("EXCEPTION CAUGHT IN ROOT:")
        traceback.print_exc()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(run_diagnostic())
