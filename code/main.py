from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import sys
sys.path.append("database")
from database.db_handler_async import AsyncDatabaseHandler
from database.db_classes import *
from database.db_pydantic_classes import *
import uvicorn
#uvicorn main:app --reload
#http://localhost:8000/docs

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

@app.post("/create_product/")
async def create_product(product: ProductBase):
    async with AsyncDatabaseHandler("Product") as db_h:
        try:
            product = await db_h.create(
                name=product.name,
                description=product.description,
                category_id=product.category_id,
                category_name=product.category_name,
                purchase_price=product.purchase_price,
                restock_price=product.restock_price,
                currency=product.currency,
                quantity=product.quantity
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to create product: {e}")
    return product

@app.post("/create_transaction/")
async def create_transaction(transaction: TransactionBase):
    async with AsyncDatabaseHandler("Transaction") as db_h:
        try:
            transaction = await db_h.create(
                product_id=transaction.product_id,
                user_id=transaction.user_id,
                currency=transaction.currency,
                quantity=transaction.quantity,
                transaction_type=transaction.transaction_type
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to create transaction: {e}")
    return transaction

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)