
import asyncio
import os
from loguru import logger
import sys

# Configure logger
logger.remove()
logger.add(sys.stderr, level="INFO")

async def verify_integration():
    logger.info("🧪 Test de l'intégration OpenRouter...")
    
    from core.agent_base import BaseAgent
    from llm.unified_client import UnifiedLLMClient
    
    # Mock class since BaseAgent is abstract
    class TestAgent(BaseAgent):
        async def think(self, task): return {}
        async def act(self, plan): return {}
    
    # 1. Test Unified Client Initialization
    client = UnifiedLLMClient()
    if client.openrouter_client:
        logger.success("✅ UnifiedLLMClient a détecté la clé OpenRouter.")
    else:
        logger.error("❌ UnifiedLLMClient n'a PAS détecté la clé OpenRouter (Vérifier .env).")
    
    # 2. Test Agent Initialization
    agent = TestAgent(name="TestRouter", model="mistralai/mistral-7b-instruct:free")
    await agent.initialize()
    
    if agent.llm_client.openrouter_client:
        logger.success(f"✅ Agent {agent.name} utilise bien le client OpenRouter.")
    else:
        logger.warning(f"⚠️ Agent {agent.name} est en mode Local uniquement.")
        
    # 3. Test Generation (ping)
    try:
        logger.info("📡 Tentative de génération via OpenRouter...")
        response = await agent.generate_response("Say 'Hello OpenRouter' in 2 words.")
        logger.success(f"✅ Réponse reçue: {response}")
    except Exception as e:
        logger.error(f"❌ Erreur de génération: {e}")

    await agent.shutdown()

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    asyncio.run(verify_integration())
