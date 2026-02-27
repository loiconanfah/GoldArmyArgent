import stripe
import os
from dotenv import load_dotenv

# Charger les clés depuis le .env
load_dotenv()
stripe.api_key = os.getenv("STRIPE_API_KEY")

def create_goldarmy_products():
    print("🚀 Démarrage de la création des produits Stripe...")
    
    products = [
        {
            "name": "GoldArmy Essentiel",
            "description": "25 recherches Sniper, 10 audits de CV, 10 entretiens RH IA.",
            "price": 999, # 9.99€ en cents
            "tier": "ESSENTIAL"
        },
        {
            "name": "GoldArmy Pro",
            "description": "Sniper illimité, 20 audits de CV, 15 entretiens RH IA, Headhunter illimité.",
            "price": 1999, # 19.99€ en cents
            "tier": "PRO"
        }
    ]
    
    new_ids = {}

    for p in products:
        try:
            # 1. Créer le produit
            product = stripe.Product.create(
                name=p["name"],
                description=p["description"],
                metadata={"tier": p["tier"]}
            )
            print(f"✅ Produit créé : {p['name']} ({product.id})")
            
            # 2. Créer le prix récurrent
            price = stripe.Price.create(
                product=product.id,
                unit_amount=p["price"],
                currency="eur",
                recurring={"interval": "month"},
                metadata={"tier": p["tier"]}
            )
            print(f"✅ Prix créé : {p['tier']} -> {price.id}")
            
            new_ids[p["tier"]] = price.id
            
        except Exception as e:
            print(f"❌ Erreur pour {p['name']}: {e}")

    print("\n📝 Nouveaux IDs à copier dans api/stripe_service.py :")
    print(new_ids)
    return new_ids

if __name__ == "__main__":
    if not stripe.api_key:
        print("❌ STRIPE_API_KEY non trouvée dans le .env")
    else:
        create_goldarmy_products()
