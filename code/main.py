from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sys
sys.path.append("database")
from database.db_handler_async import AsyncDatabaseHandler
from database.db_classes import *
from database.db_pydantic_classes import *
from typing import List, Annotated
import uvicorn
from werkzeug.security import check_password_hash
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

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.post("/login_user/", response_model=LoginResponse)
async def login_user(user: LoginBase):
    async with AsyncDatabaseHandler() as db_h:
        try:
            user_db = await db_h.get_by(User, username=user.username)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to login user: {e}")
        
    if user_db is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not check_password_hash(user_db.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid password")
    
    # Create a dictionary of user_db fields, excluding SQLAlchemy-specific fields
    user_dict = {k: v for k, v in user_db.__dict__.items() if not k.startswith('_')}
    
    user_response = LoginResponse(**user_dict)
    return user_response

# User Creator
# UserResponse model removes password from response
@app.post("/create_user/", response_model=UserResponse) 
async def create_user(user: UserBase):
    async with AsyncDatabaseHandler("User") as db_h:
        try:
            user = await db_h.create(
                username=user.username,
                password=user.password,
                email=user.email
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to create user: {e}")
    user_response = UserResponse(**user.__dict__)
    return user_response

# AdminUserResponse model removes password from response
@app.post("/create_admin_user/", response_model=AdminUserResponse) 
async def create_admin_user(admin_user: AdminUserBase):
    async with AsyncDatabaseHandler("AdminUser") as db_h:
        try:
            admin_user = await db_h.create(
                username=admin_user.username,
                password=admin_user.password,
                email=admin_user.email,
                admin_status=admin_user.admin_status
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to create admin user: {e}")
    admin_user_response = AdminUserResponse(**admin_user.__dict__)
    return admin_user_response

# User Delete
@app.delete("/delete_user/{user_id}/")
async def delete_user(user_id: int):
    async with AsyncDatabaseHandler("User") as db_h:
        try:
            await db_h.delete(User, id=user_id)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to delete user: {e}")
    return {"detail": "User deleted"}

# AdminUser Delete
@app.delete("/delete_admin_user/{user_id}/")
async def delete_admin_user(user_id: int):
    async with AsyncDatabaseHandler("AdminUser") as db_h:
        try:
            await db_h.delete(AdminUser, id=user_id)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to delete admin user: {e}")
    return {"detail": "Admin user deleted"}

# User Update
@app.put("/update_user/{user_id}/")
async def update_user(user_id: int, user: UserBase):
    async with AsyncDatabaseHandler("User") as db_h:
        try:
            await db_h.update(User, id=user_id, **user.dict())
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to update user: {e}")
    return {"detail": "User updated"}

# User Getters
@app.get("/get_user/{user_id}/", response_model=UserResponse)
async def get_user(user_id: int):
    async with AsyncDatabaseHandler() as db_h:
        try:
            user = await db_h.get_by(User, id=user_id)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to get user: {e}")
        
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_response = UserResponse(**user.__dict__)
    return user_response

@app.get("/get_user_by_username/{username}/", response_model=UserResponse)
async def get_user_by_username(username: str):
    async with AsyncDatabaseHandler() as db_h:
        try:
            user = await db_h.get_by(User, username=username)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to get user: {e}")
        
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_response = UserResponse(**user.__dict__)
    return user_response

@app.get("/get_users/", response_model=List[UserResponse])
async def get_users():
    async with AsyncDatabaseHandler() as db_h:
        try:
            users = await db_h.get_all(User)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to get users: {e}")
    
    if users is None:
        raise HTTPException(status_code=404, detail="No users found")

    user_responses = [UserResponse(**user.__dict__) for user in users]
    return user_responses

@app.get("/get_admin_users/", response_model=List[AdminUserResponse])
async def get_admin_users():
    async with AsyncDatabaseHandler() as db_h:
        try:
            admin_users = await db_h.get_all(AdminUser)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to get admin users: {e}")
        
    if admin_users is None:
        raise HTTPException(status_code=404, detail="No users found")
    
    admin_user_responses = [AdminUserResponse(**admin_user.__dict__) for admin_user in admin_users]
    return admin_user_responses

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
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to create category: {e}")
    return category

# Category Delete
@app.delete("/delete_category/{category_id}/")
async def delete_category(category_id: int):
    async with AsyncDatabaseHandler("Category") as db_h:
        try:
            await db_h.delete(Category, id=category_id)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to delete category: {e}")
    return {"detail": "Category deleted"}

# Category Update
@app.put("/update_category/{category_id}/")
async def update_category(category_id: int, category: CategoryBase):
    async with AsyncDatabaseHandler("Category") as db_h:
        try:
            await db_h.update(Category, id=category_id, **category.dict())
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to update category: {e}")
    return {"detail": "Category updated"}

# Category Getters
@app.get("/get_category/{category_id}/")
async def get_category(category_id: int):
    async with AsyncDatabaseHandler() as db_h:
        try:
            category = await db_h.get_by(Category, id=category_id)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to get category: {e}")
        
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    return category

@app.get("/get_category_by_name/{category_name}/")
async def get_category_by_name(category_name: str):
    async with AsyncDatabaseHandler() as db_h:
        try:
            category = await db_h.get_by(Category, name=category_name)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to get category: {e}")
        
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return category

@app.get("/get_subcategories/{category_name}/")
async def get_subcategories(category_name: str):
    async with AsyncDatabaseHandler() as db_h:
        try:
            category = await db_h.get_by(Category, name=category_name)
            if category is None:
                raise HTTPException(status_code=404, detail="Category not found")
            subcategories = await db_h.get_all_by(Category, parent_id=category.id)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to get subcategories: {e}")
        
    if subcategories is None:
        raise HTTPException(status_code=404, detail="No subcategories found")            

    return subcategories

@app.get("/get_categories/")
async def get_categories():
    async with AsyncDatabaseHandler() as db_h:
        try:
            categories = await db_h.get_all(Category)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to get categories: {e}")
        
    if categories is None:
        raise HTTPException(status_code=404, detail="No categories found")

    return categories

# Product Creator
@app.post("/create_product/")
async def create_product(product: ProductBase):
    async with AsyncDatabaseHandler("Product") as db_h:
        try:
            product = await db_h.create(
                name=product.name,
                description=product.description,
                category_name=product.category_name,
                purchase_price=product.purchase_price,
                restock_price=product.restock_price,
                currency=product.currency,
                quantity=product.quantity
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to create product: {e}")
    return product

# Product Delete
@app.delete("/delete_product/{product_id}/")
async def delete_product(product_id: int):
    async with AsyncDatabaseHandler("Product") as db_h:
        try:
            await db_h.delete_by_id(Product, product_id)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to delete product: {e}")
    return {"detail": "Product deleted"}

# Product Update
@app.put("/update_product/{product_id}/")
async def update_product(product_id: int, product: ProductBase):
    async with AsyncDatabaseHandler("Product") as db_h:
        try:
            await db_h.update(Product, id=product_id, **product.dict())
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to update product: {e}")
    return {"detail": "Product updated"}

# Product Getters
@app.get("/get_product/{product_id}/")
async def get_product(product_id: int):
    async with AsyncDatabaseHandler() as db_h:
        try:
            product = await db_h.get_by(Product, id=product_id)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to get product: {e}")
        
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return product

@app.get("/get_product_by_name/{product_name}/")
async def get_product_by_name(product_name: str):
    async with AsyncDatabaseHandler() as db_h:
        try:
            product = await db_h.get_by(Product, name=product_name)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to get product: {e}")
        
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return product

@app.get("/get_products_by_category/{category_name}/")
async def get_products_by_category(category_name: str):
    async with AsyncDatabaseHandler() as db_h:
        try:
            category = await db_h.get_by(Category, name=category_name)
            if category is None:
                raise HTTPException(status_code=404, detail="Category not found")
            products = await db_h.get_all_by(Product, category_id=category.id)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to get products: {e}")
        
    if products is None:
        raise HTTPException(status_code=404, detail="No products found")

    return products

async def get_products_in_category_and_subcategories(db_h, category_id):
    products = await db_h.get_all_by(Product, category_id=category_id)
    subcategories = await db_h.get_all_by(Category, parent_id=category_id)
    for subcategory in subcategories:
        products += await get_products_in_category_and_subcategories(db_h, subcategory.id)
    return products

@app.get("/get_products_by_category_with_subcategories/{category_name}/")
async def get_products_by_category_with_subcategories(category_name: str):
    async with AsyncDatabaseHandler() as db_h:
        try:
            category = await db_h.get_by(Category, name=category_name)
            if category is None:
                raise HTTPException(status_code=404, detail="Category not found")
            products = await get_products_in_category_and_subcategories(db_h, category.id)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to get products: {e}")
        
    if products is None:
        raise HTTPException(status_code=404, detail="No products found")

    return products

@app.get("/get_products_with_quantity_less_than/{quantity}/")
async def get_products_with_quantity_less_than(quantity: int):
    async with AsyncDatabaseHandler() as db_h:
        try:
            products = await db_h.get_all_with_condition(Product, Product.quantity < quantity)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to get products: {e}")
        
    if products is None:
        raise HTTPException(status_code=404, detail="No products found")
    
    return products

@app.get("/get_products/")
async def get_products():
    async with AsyncDatabaseHandler() as db_h:
        try:
            products = await db_h.get_all(Product)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to get products: {e}")
        
    if products is None:
        raise HTTPException(status_code=404, detail="No products found")

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
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to create transaction: {e}")
    return transaction

# Transaction Delete
@app.delete("/delete_transaction/{transaction_id}/")
async def delete_transaction(transaction_id: int):
    async with AsyncDatabaseHandler("Transaction") as db_h:
        try:
            await db_h.delete(Transaction, id=transaction_id)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to delete transaction: {e}")
    return {"detail": "Transaction deleted"}

# Transaction Update
@app.put("/update_transaction/{transaction_id}/")
async def update_transaction(transaction_id: int, transaction: TransactionBase):
    async with AsyncDatabaseHandler("Transaction") as db_h:
        try:
            await db_h.update(Transaction, id=transaction_id, **transaction.dict())
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to update transaction: {e}")
    return {"detail": "Transaction updated"}

# Transaction Getters
@app.get("/get_transaction/{transaction_id}/")
async def get_transaction(transaction_id: int):
    async with AsyncDatabaseHandler() as db_h:
        try:
            transaction = await db_h.get_by(Transaction, id=transaction_id)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to get transaction: {e}")
        
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return transaction

@app.get("/get_transactions_by_user_id/{user_id}/")
async def get_transactions_by_user(user_id: int):
    async with AsyncDatabaseHandler() as db_h:
        try:
            transactions = await db_h.get_all_by(Transaction, user_id=user_id)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to get transactions: {e}")
        
    if transactions is None:
        raise HTTPException(status_code=404, detail="No transactions found")

    return transactions

@app.get("/get_transactions_by_user_name/{user_name}/")
async def get_transactions_by_user(user_name: str):
    async with AsyncDatabaseHandler() as db_h:
        try:
            user = await db_h.get_by(User, username=user_name)
            if user is None:
                raise HTTPException(status_code=404, detail="User not found")
            transactions = await db_h.get_all_by(Transaction, user_id=user.id)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to get transactions: {e}")
        
    if transactions is None:
        raise HTTPException(status_code=404, detail="No transactions found")

    return transactions

@app.get("/get_transactions_by_product_id/{product_id}/")
async def get_transactions_by_product(product_id: int):
    async with AsyncDatabaseHandler() as db_h:
        try:
            transactions = await db_h.get_all_by(Transaction, product_id=product_id)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to get transactions: {e}")
        
    if transactions is None:
        raise HTTPException(status_code=404, detail="No transactions found")
    
    return transactions

@app.get("/get_transactions_by_product_name/{product_name}/")
async def get_transactions_by_product(product_name: str):
    async with AsyncDatabaseHandler() as db_h:
        try:
            product = await db_h.get_by(Product, name=product_name)
            if product is None:
                raise HTTPException(status_code=404, detail="Product not found")
            transactions = await db_h.get_all_by(Transaction, product_id=product.id)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to get transactions: {e}")
        
    if transactions is None:
        raise HTTPException(status_code=404, detail="No transactions found")

    return transactions
@app.get("/get_transactions_by_transaction_type/{transaction_type}/")
async def get_transactions_by_transaction_type(transaction_type: str):
    async with AsyncDatabaseHandler() as db_h:
        try:
            transactions = await db_h.get_all_by(Transaction, transaction_type=transaction_type)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to get transactions: {e}")
        
    if transactions is None:
        raise HTTPException(status_code=404, detail="No transactions found")

    return transactions

@app.get("/get_transactions/")
async def get_transactions():
    async with AsyncDatabaseHandler() as db_h:
        try:
            transactions = await db_h.get_all(Transaction)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to get transactions: {e}")
        
    if transactions is None:
        raise HTTPException(status_code=404, detail="No transactions found")

    return transactions


#get logs
@app.get("/get_logs/")
async def get_logs():
    async with AsyncDatabaseHandler() as db_h:
        try:
            logs = await db_h.get_all(Log)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to get logs: {e}")
        
    if logs is None:
        raise HTTPException(status_code=404, detail="No logs found")

    return logs

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)