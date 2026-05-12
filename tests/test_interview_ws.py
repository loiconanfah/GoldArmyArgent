import asyncio
import websockets
import json

async def test_ws():
    # Remplacer par un token valide si on veut passer la première étape, 
    # ou on peut laisser vide pour voir si c'est bien l'auth qui bloque en premier.
    uri = "ws://localhost:8000/api/interview/ws?token=invalid_for_test"
    try:
        async with websockets.connect(uri) as websocket:
            print("Connecté.")
            # Attendre la première trame
            response = await websocket.recv()
            print(f"Reçu: {response}")
            
            # Envoyer le payload setup
            setup_payload = {
                "type": "setup",
                "payload": {
                    "cv": "Test CV",
                    "jobTitle": "Dev",
                    "company": "Test Co",
                    "jobDetails": "Test détails",
                    "interviewType": "general",
                    "recruiterId": "tech"
                }
            }
            await websocket.send(json.dumps(setup_payload))
            print("Setup envoyé.")
            
            while True:
                response = await websocket.recv()
                print(f"Reçu en boucle: {response}")
                
    except websockets.exceptions.ConnectionClosed as e:
        print(f"Fermé avec le code {e.code}, raison: {e.reason}")
    except Exception as e:
        print(f"Erreur globale: {e}")

asyncio.run(test_ws())
