from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import sys
sys.path.append("database")
from database.db_handler_async import AsyncDatabaseHandler
from database.db_classes import *
from database.db_pydantic_classes import *
from typing import List, Annotated
import uvicorn
#uvicorn main:app --reload
#npx create-react-app storage-app
#http://localhost:8000/docs

app = FastAPI()

origins = [
    "http://localhost:3000",  # React's default port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# User Creator
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

# User Getters
@app.get("/get_user/{user_id}")
async def get_user(user_id: int):
    async with AsyncDatabaseHandler() as db_h:
        try:
            user = await db_h.get_by(User, id=user_id)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to get user: {e}")
    return user

@app.get("/get_user_by_username/{username}")
async def get_user_by_username(username: str):
    async with AsyncDatabaseHandler() as db_h:
        try:
            user = await db_h.get_by(User, username=username)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to get user: {e}")
    return user

@app.get("/get_users/")
async def get_users():
    async with AsyncDatabaseHandler() as db_h:
        try:
            users = await db_h.get_all(User)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to get users: {e}")
    return users

# Category Creator
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

# Category Getters
@app.get("/get_category/{category_id}")
async def get_category(category_id: int):
    async with AsyncDatabaseHandler() as db_h:
        try:
            category = await db_h.get_by(Category, id=category_id)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to get category: {e}")
    return category

@app.get("/get_category_by_name/{category_name}")
async def get_category_by_name(category_name: str):
    async with AsyncDatabaseHandler() as db_h:
        try:
            category = await db_h.get_by(Category, name=category_name)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to get category: {e}")
    return category

@app.get("/get_subcategories/{category_name}")
async def get_subcategories(category_name: str):
    async with AsyncDatabaseHandler() as db_h:
        try:
            category = await db_h.get_by(Category, name=category_name)
            subcategories = await db_h.get_all_by(Category, parent_id=category.id)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to get subcategories: {e}")
    return subcategories

@app.get("/get_categories/")
async def get_categories():
    async with AsyncDatabaseHandler() as db_h:
        try:
            categories = await db_h.get_all(Category)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to get categories: {e}")
    return categories

# Product Creator
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

# Product Getters
@app.get("/get_product/{product_id}")
async def get_product(product_id: int):
    async with AsyncDatabaseHandler() as db_h:
        try:
            product = await db_h.get_by(Product, id=product_id)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to get product: {e}")
    return product

@app.get("/get_product_by_name/{product_name}")
async def get_product_by_name(product_name: str):
    async with AsyncDatabaseHandler() as db_h:
        try:
            product = await db_h.get_by(Product, name=product_name)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to get product: {e}")
    return product

@app.get("/get_products_by_category/{category_name}")
async def get_products_by_category(category_name: str):
    async with AsyncDatabaseHandler() as db_h:
        try:
            category = await db_h.get_by(Category, name=category_name)
            products = await db_h.get_all_by(Product, category_id=category.id)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to get products: {e}")
    return products

async def get_products_in_category_and_subcategories(db_h, category_id):
    products = await db_h.get_all_by(Product, category_id=category_id)
    subcategories = await db_h.get_all_by(Category, parent_id=category_id)
    for subcategory in subcategories:
        products += await get_products_in_category_and_subcategories(db_h, subcategory.id)
    return products

@app.get("/get_products_by_category_with_subcategories/{category_name}")
async def get_products_by_category_with_subcategories(category_name: str):
    async with AsyncDatabaseHandler() as db_h:
        try:
            category = await db_h.get_by(Category, name=category_name)
            products = await get_products_in_category_and_subcategories(db_h, category.id)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to get products: {e}")
    return products

@app.get("/get_products_with_quantity_less_than/{quantity}")
async def get_products_with_quantity_less_than(quantity: int):
    async with AsyncDatabaseHandler() as db_h:
        try:
            products = await db_h.get_all_with_condition(Product, Product.quantity < quantity)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to get products: {e}")
    return products

@app.get("/get_products/")
async def get_products():
    async with AsyncDatabaseHandler() as db_h:
        try:
            products = await db_h.get_all(Product)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to get products: {e}")
    return products

# Transaction Creator
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

# Transaction Getters
@app.get("/get_transaction/{transaction_id}")
async def get_transaction(transaction_id: int):
    async with AsyncDatabaseHandler() as db_h:
        try:
            transaction = await db_h.get_by(Transaction, id=transaction_id)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to get transaction: {e}")
    return transaction

@app.get("/get_transactions_by_user_id/{user_id}")
async def get_transactions_by_user(user_id: int):
    async with AsyncDatabaseHandler() as db_h:
        try:
            transactions = await db_h.get_all_by(Transaction, user_id=user_id)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to get transactions: {e}")
    return transactions

@app.get("/get_transactions_by_user_name/{user_name}")
async def get_transactions_by_user(user_name: str):
    async with AsyncDatabaseHandler() as db_h:
        try:
            user = await db_h.get_by(User, username=user_name)
            transactions = await db_h.get_all_by(Transaction, user_id=user.id)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to get transactions: {e}")
    return transactions

@app.get("/get_transactions_by_product_id/{product_id}")
async def get_transactions_by_product(product_id: int):
    async with AsyncDatabaseHandler() as db_h:
        try:
            transactions = await db_h.get_all_by(Transaction, product_id=product_id)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to get transactions: {e}")
    return transactions

@app.get("/get_transactions_by_product_name/{product_name}")
async def get_transactions_by_product(product_name: str):
    async with AsyncDatabaseHandler() as db_h:
        try:
            product = await db_h.get_by(Product, name=product_name)
            transactions = await db_h.get_all_by(Transaction, product_id=product.id)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to get transactions: {e}")
    return transactions

@app.get("/get_transactions_by_transaction_type/{transaction_type}")
async def get_transactions_by_transaction_type(transaction_type: str):
    async with AsyncDatabaseHandler() as db_h:
        try:
            transactions = await db_h.get_all_by(Transaction, transaction_type=transaction_type)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to get transactions: {e}")
    return transactions

@app.get("/get_transactions/")
async def get_transactions():
    async with AsyncDatabaseHandler() as db_h:
        try:
            transactions = await db_h.get_all(Transaction)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to get transactions: {e}")
    return transactions

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)