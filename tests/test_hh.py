import asyncio
from agents.headhunter import headhunter_agent

async def main():
    await headhunter_agent.initialize()
    print("Testing headhunter agent with icebergfinance...")
    res = await headhunter_agent.find_decision_makers({'company_name': 'icebergfinance'})
    print(res)

if __name__ == "__main__":
    asyncio.run(main())
