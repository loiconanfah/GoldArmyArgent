import asyncio
from agents.headhunter import headhunter_agent
import time

async def main():
    print("Testing Headhunter with 'Google'...")
    await headhunter_agent.initialize()
    start_time = time.time()
    res = await headhunter_agent.find_decision_makers({"company_name": "Google"})
    print(f"Results (took {time.time() - start_time:.2f}s):", res)

if __name__ == "__main__":
    asyncio.run(main())
