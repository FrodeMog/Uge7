from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware

import sys
sys.path.append("database")
from database.db_handler_async import AsyncDatabaseHandler
from database.db_classes import *
from database.db_pydantic_classes import *

import uvicorn

app = FastAPI()

origins = [
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
)

#curl -X POST -H "Content-Type: application/json" -d "{\"username\": \"test\", \"password\": \"test\", \"email\": \"test@example.com\"}" http://localhost:8000/create_user/
@app.post("/create_user/")
async def create_user(user: UserBase):
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

#curl -X POST -H "Content-Type: application/json" -d "{\"username\": \"testadmin\", \"password\": \"test\", \"email\": \"testadmin@example.com\", \"admin_status\": \"full\"}" http://localhost:8000/create_admin_user/
@app.post("/create_admin_user/")
async def create_admin_user(admin_user: AdminUserBase):
    async with AsyncDatabaseHandler("AdminUser") as db_h:
        try:
            admin_user = await db_h.create(
                username=admin_user.username,
                password=admin_user.password,
                email=admin_user.email,
                admin_status=admin_user.admin_status
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to create admin user: {e}")
    return admin_user

#curl -X POST -H "Content-Type: application/json" -d "{\"name\": \"curl_test\", \"description\": \"test\", \"parent_id\": 1, \"parent_name\": \"test\"}" http://localhost:8000/create_category/
@app.post("/create_category/")
async def create_category(category: CategoryBase):
    async with AsyncDatabaseHandler("Category") as db_h:
        try:
            category = await db_h.create(
                name=category.name,
                description=category.description,
                parent_id=category.parent_id,
                parent_name=category.parent_name
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to create category: {e}")
    return category

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)