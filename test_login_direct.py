import asyncio
from fastapi.security import OAuth2PasswordRequestForm
from api.auth import login
from core.database import init_db

async def test():
    await init_db()
    
    class MockForm:
        def __init__(self, username, password):
            self.username = username
            self.password = password
            self.scopes = []
            self.client_id = None
            self.client_secret = None
            
    form = MockForm("yayzoy@gmail.com", "password")
    
    try:
        res = await login(form)
        print("Success:", res)
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
