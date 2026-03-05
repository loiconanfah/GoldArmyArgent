import httpx
import asyncio

async def submit_indexnow(host: str, url_list: list[str]):
    """
    Soumet une liste d'URLs à l'API IndexNow de Bing.
    """
    key = "11e1c9334650482a8036bf554489f586"
    key_location = f"https://{host}/{key}.txt"
    payload = {
        "host": host,
        "key": key,
        "keyLocation": key_location,
        "urlList": url_list
    }
    
    print(f"Soumission pour {host} avec la clé {key}...")
    headers = {"Content-Type": "application/json; charset=utf-8"}
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.indexnow.org/IndexNow", 
            json=payload,
            headers=headers
        )
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("Succès ! URLs soumises avec succès.")
        elif response.status_code == 202:
            print("Accepté. Le traitement est en cours.")
        else:
            print("Erreur ou refus. Détails :")
        
        try:
            print(f"Réponse JSON: {response.json()}")
        except:
            print(f"Réponse Texte: {response.text}")

if __name__ == "__main__":
    # Remplacer par le vrai domaine
    my_host = "ton_domaine_ici.com"
    my_urls = [
        f"https://{my_host}/",
        f"https://{my_host}/about",
        f"https://{my_host}/contact"
    ]
    
    if my_host == "ton_domaine_ici.com":
        print("Veuillez modifier 'my_host' et 'my_urls' dans le script avant de l'exécuter.")
    else:
        asyncio.run(submit_indexnow(my_host, my_urls))
