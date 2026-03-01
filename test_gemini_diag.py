import asyncio
import os
import sys
from dotenv import load_dotenv

# Ajouter le chemin racine pour importer les modules
sys.path.append(os.getcwd())

from llm.gemini_client import GeminiClient

async def test_gemini():
    load_dotenv()
    print(f"Clé API trouvée: {'Oui' if os.getenv('GEMINI_API_KEY') else 'Non'}")
    
    try:
        client = GeminiClient()
        print("Initialisation du client... OK")
        
        prompt = "Réponds juste 'L'armée de l'air est prête' si tu m'entends."
        print(f"Envoi du prompt: {prompt}")
        
        response = await client.generate(prompt)
        print(f"Réponse de Gemini: {response}")
        
        if "prête" in response.lower():
            print("✅ TEST GEMINI RÉUSSI")
        else:
            print("⚠️ Réponse inattendue mais l'API a répondu.")
            
    except Exception as e:
        print(f"❌ TEST GEMINI ÉCHOUÉ: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_gemini())
