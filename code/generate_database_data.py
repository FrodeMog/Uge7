from faker import Faker as fk
import sys
sys.path.append("database")
from database.db_handler_async import AsyncDatabaseHandler
from database.db_classes import *
import logging
import os
import random


logging.basicConfig(level=logging.ERROR)
os.environ['PYTHONASYNCIODEBUG'] = '1'

#python generate_database_data.py

class CleanDatabase():
    def __init__(self, session):
        self.engine = session.get_bind()
        self.session = session

    async def clean(self):
        await self.session.run_sync(self._drop_and_create_all)

    def _drop_and_create_all(self, sync_session):
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)

class GenerateFakeData():
    def __init__(self, session):
        self.session = session

    async def generate(self):
        print("Generating fake data...")
        await self.generate_references()
        await self.generate_base_users()

        await self.generate_user(100)
        await self.generate_categories(10)
        await self.generate_subcategories(100)
        await self.generate_products(100)
        await self.generate_transactions(1000)

    async def generate_references(self):
        #create a reference to deleted users
        async with AsyncDatabaseHandler("User") as db_h:
            try:
                deleted_user = await db_h.create(
                        username="deleted_user",
                        password="deleted_user",
                        email="a@a.com")
            except Exception as e:
                logging.error(e)
                print("Failed to create deleted user")
        print("Created deleted user rerefence")

        #create a reference to deleted categories
        async with AsyncDatabaseHandler("Category") as db_h:
            try:
                deleted_category = await db_h.create(name="deleted_category",
                        description="This is a placeholder for a deleted category")
            except Exception as e:
                logging.error(e)
                print("Failed to create deleted category")
        print("Created deleted category reference")

        #create a reference to deleted products
        async with AsyncDatabaseHandler("Product") as db_h:
            try:
                deleted_product = await db_h.create(
                        name="deleted_product",
                        description="This is a placeholder for a deleted product",
                        category_name="deleted_category",
                        purchase_price=1,
                        restock_price=1,
                        currency="USD",
                        quantity=0
                    )
            except Exception as e:
                logging.error(e)
                print("Failed to create deleted product")
        print("Created deleted product reference")
        
    async def generate_base_users(self):
        async with AsyncDatabaseHandler("User") as db_h:
            try:
                user = await db_h.create(
                    username="user",
                    password="user",
                    email="user@user.com"
                )
            except Exception as e:
                logging.error(e)
                self.fail("Failed to create user")
        print("Created base user")

        async with AsyncDatabaseHandler("AdminUser") as db_h:
            try:
                user = await db_h.create(
                    username="admin",
                    password="admin",
                    email="admin@admin.com",
                    admin_status="full"
                )
            except Exception as e:
                logging.error(e)
                self.fail("Failed to create admin user")
        print("Created base admin user")

    async def generate_user(self, n):
        fake = fk()
        async with AsyncDatabaseHandler("User") as db_h:
            try:
                for _ in range(n):
                    user = await db_h.create(
                        username=fake.user_name(),
                        password=fake.password(),
                        email=fake.email()
                    )
            except Exception as e:
                logging.error(e)
                print("Failed to create user")
        print(f"Generated {n} users")
        
    async def generate_categories(self, n):
        fake = fk()
        async with AsyncDatabaseHandler("Category") as db_h:
            try:
                for _ in range(n):
                    category = await db_h.create(name=fake.word(), description=fake.text())
            except Exception as e:
                logging.error(e)
                print("Failed to create category")
        print(f"Generated {n} categories")

    async def generate_subcategories(self, n):
        fake = fk()
        async with AsyncDatabaseHandler("Category") as db_h:
            try:
                # Get all categories
                categories = await db_h.get_all(Category)
                for _ in range(n):
                    # Select a random category
                    category = random.choice(categories)
                    subcategory = await db_h.create(name=fake.word(), description=fake.text(), parent_id=category.id)
            except Exception as e:
                logging.error(e)
                print("Failed to create subcategory")
        print(f"Generated {n} subcategories")

    async def generate_products(self, n):
        fake = fk()
        async with AsyncDatabaseHandler("Product") as db_h:
            try:
                # Get all categories
                categories = await db_h.get_all(Category)
                for _ in range(n):
                    # Select a random category
                    category = random.choice(categories)
                    fake_name = fake.word()
                    # Check if a product with the same name already exists
                    existing_product = await db_h.get_by(Product, name=fake_name)
                    if existing_product:
                        print(f"A product with the name {fake_name} already exists. Skipping...")
                        continue
                    fake_purchase_price = fake.random_int(10, 100)
                    fake_restock_price = fake_purchase_price - fake.random_int(1, 9)
                    product = await db_h.create(
                        name=fake_name,
                        description=fake.text(),
                        category_name=category.name,  # Use category name instead of id
                        purchase_price=fake_purchase_price,
                        restock_price=fake_restock_price,
                        currency=fake.random_element(elements=ALLOWED_CURRENCIES),
                        quantity=fake.random_int(20, 1000)
                    )
            except Exception as e:
                logging.error(e)
                print("Failed to create product")
        print(f"Generated {n} products")

    async def generate_transactions(self, n):
        fake = fk()
        async with AsyncDatabaseHandler("Product") as db_h:
            try:
                # Get all products
                products = await db_h.get_all(Product)
            except Exception as e:
                logging.error(e)
                print("Failed to get products")
        async with AsyncDatabaseHandler("User") as db_h:
            try:
                # Get all users
                users = await db_h.get_all(User)
            except Exception as e:
                logging.error(e)
                print("Failed to get users")
        async with AsyncDatabaseHandler("Transaction") as db_h:
            admin_user = await db_h.get_by(User, username="admin")
            for _ in range(n):
                try:
                    product = random.choice(products)
                    #skip deleted reference product
                    if product.id == 1:
                        continue
                    transaction_type = random.choice(["purchase", "restock"])
                    if transaction_type == "purchase":
                        user = random.choice(users)
                    else:  # restock
                        user = admin_user
                    transaction = await db_h.create(
                        product_id=product.id,
                        user_id=user.id,
                        transaction_type=transaction_type,
                        quantity=fake.random_int(1, 10),
                        currency=fake.random_element(elements=ALLOWED_CURRENCIES)
                    )
                except Exception as e:
                    logging.error(e)
                    print("Failed to create transaction")

        print(f"Generated {n} transactions")


if __name__ == "__main__":
    async def main():
        async with AsyncDatabaseHandler() as db_h:
            cleaner = CleanDatabase(db_h.session)
            await cleaner.clean()
            generator = GenerateFakeData(db_h.session)
            await generator.generate()
    
    import asyncio
    asyncio.run(main())