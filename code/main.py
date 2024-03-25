from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware

import sys
sys.path.append("database")
from database.db_handler_async import AsyncDatabaseHandler
from database.db_classes import *

import uvicorn

app = FastAPI()

origins = [
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
)

class CleanDatabase():
    def __init__(self, session):
        self.engine = session.get_bind()
        self.session = session

    async def create_tables(self):
        await self.session.run_sync(self.create_all)

    def _create_all(self, sync_session):
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)

with AsyncDatabaseHandler() as db_h:
    cleaner = CleanDatabase(db_h.session)
    cleaner.create_tables()

@app.post("/create_user/")
async def create_user(user: User):
    async with AsyncDatabaseHandler("User") as db_h:
        try:
            user = await db_h.create(
                username=user.username,
                password=user.password,
                email=user.email
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to create user: {e}")
    return user

#@app.get("/")
#def read_root():
#    return {"Hello": "World"}
#
#@app.get("/items/{item_id}")
#def read_item(item_id: int, q: str = None):
#    return {"item_id": item_id, "q": q}

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)