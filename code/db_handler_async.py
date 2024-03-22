from db_classes import *
from db_decorators import log_to_db, handle_exceptions_and_rollback
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

class AsyncDatabaseHandler():
    def __init__(self, session):
        super().__init__()
        self.session = session

    async def add(self, instance):
        self.session.add(instance)
        await self.session.commit()

    async def delete(self, instance):
        self.session.delete(instance)
        await self.session.commit()

    async def update(self, instance, **kwargs):
        self.session.query(instance).update(kwargs)
        await self.session.commit()

    async def commit(self):
        try:
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            raise e
        finally:
            await self.session.close()

    async def rollback(self):
        await self.session.rollback()
    
    async def close(self):
        await self.session.close()

    async def get_by_id(self, model, id):
        return await self.session.execute(select(model).filter(model.id == id)).scalars().first()
    
    async def get_by(self, model, **filters):
        stmt = select(model).where(*[getattr(model, k) == v for k, v in filters.items()])
        result = await self.session.execute(stmt)
        return result.scalars().one_or_none()

    async def get_all(self, model):
        return await self.session.execute(select(model)).scalars().all()

    async def get_all_by(self, model, **filters):
        return await self.session.execute(select(model).filter_by(**filters)).scalars().all()

class AsyncCategoryHandler(AsyncDatabaseHandler):
    @handle_exceptions_and_rollback
    @log_to_db
    async def create_category(self, name, description, parent_id=None, parent_name=None):
        # Check if there are any categories in the database
        if not await self.get_all(Category):
            # If not, create the "Unknown" category
            unknown_category = Category(name="Unknown", description="Unknown category. Reference for products with no category assigned.")
            await self.add(unknown_category)
            await self.commit()

        parent = None
        if parent_id is not None:
            parent = await self.get_by(Category, id=parent_id)
            if parent is None:
                raise ValueError(f"No category found with ID {parent_id}")
        elif parent_name is not None:
            parent = await self.get_by(Category, name=parent_name)
            if parent is None:
                parent = Category(name=parent_name)
                await self.add(parent)
                await self.commit()

        category = Category(
            name=name,
            description=description,
            parent_id=parent.id if parent else None
        )
        await self.add(category)
        await self.commit()
        return category
    
    @handle_exceptions_and_rollback
    @log_to_db
    async def update_category(self, category_id, **kwargs):
        category = await self.get_by(Category, id=category_id)
        if category:
            for key, value in kwargs.items():
                setattr(category, key, value)
            await self.commit()
        return category
    
    @handle_exceptions_and_rollback
    @log_to_db
    async def delete_category(self, category_id):
        category = await self.get_by_id(Category, category_id)
        if category:
            self.delete(category)
            await self.commit()
        return category

class AsyncProductHandler(AsyncDatabaseHandler):
    @handle_exceptions_and_rollback
    @log_to_db
    async def create_product(self, name, description, purchase_price, restock_price, currency, quantity, category_id=None, category_name=None):
        if category_name is not None:
            category = await self.get_by(Category, name=category_name)
            if category is None:
                category = Category(name=category_name)
                await self.add(category)
                await self.commit()
        elif category_id is not None:
            category = await self.get_by(Category, id=category_id)
            if category is None:
                raise ValueError(f"No category found with ID {category_id}")
        else:
            category = await self.get_by(Category, id=1)  # Use the default "Unknown" category

        product = Product(
            name=name,
            description=description,
            category_id=category.id,
            purchase_price=purchase_price,
            restock_price=restock_price,
            currency=currency,
            quantity=quantity,
            creation_date=datetime.now(),
            changed_date=datetime.now()
        )
        await self.add(product)
        await self.commit()
        return product

    @handle_exceptions_and_rollback
    @log_to_db
    async def update_product(self, product_id, **kwargs):
        product = await self.get_by(Product, id=product_id)
        if product:
            for key, value in kwargs.items():
                setattr(product, key, value)
            product.changed_date = datetime.now()
            await self.commit()
        return product
    
    @handle_exceptions_and_rollback
    @log_to_db
    async def delete_product(self, product_id):
        product = await self.get_by_id(Product, product_id)
        if product:
            self.delete(product)
            await self.commit()
        return product

class AsyncTransactionHandler(AsyncDatabaseHandler):
    @handle_exceptions_and_rollback
    @log_to_db
    async def create_transaction(self, product_id, user_id, quantity, transaction_type, currency):
        product = await self.get_by(Product, id=product_id)
        if product is None:
            raise ValueError(f"No product found with ID {product_id}")

        if transaction_type == 'purchase':
            if product.quantity < quantity:
                raise ValueError("Not enough stock for purchase")
            product.quantity -= quantity
            price = product.purchase_price * quantity
        elif transaction_type == 'refund':
            product.quantity += quantity
            price = -product.purchase_price * quantity
        elif transaction_type == 'restock':
            product.quantity += quantity
            price = -product.restock_price * quantity
        else:
            raise ValueError("Invalid transaction type")

        transaction = Transaction(
            product_id=product_id,
            user_id=user_id,
            price=price,
            quantity=quantity,
            transaction_type=transaction_type,
            currency=currency
        )
        await self.add(transaction)
        await self.commit()
        return transaction

class AsyncUserHandler(AsyncDatabaseHandler):
    @handle_exceptions_and_rollback
    @log_to_db
    async def create_user(self, username, password, email):
        existing_user_with_same_username = await self.get_by(User, username=username)
        if existing_user_with_same_username is not None:
            raise ValueError("A user with this username already exists")

        existing_user_with_same_email = await self.get_by(User, email=email)
        if existing_user_with_same_email is not None:
            raise ValueError("A user with this email already exists")

        user = User()
        user.set_username(username)
        user.set_email(email)
        user.set_password(password)
        await self.add(user)
        await self.commit()
        return user
        
    @handle_exceptions_and_rollback
    @log_to_db
    async def update_user(self, user_id, **kwargs):
        user = await self.get_by(User, id=user_id)
        if user:
            for key, value in kwargs.items():
                setattr(user, key, value)
            await self.commit()
        return user
    
    @handle_exceptions_and_rollback
    @log_to_db
    async def delete_user(self, user_id):
        user = await self.get_by_id(User, user_id)
        if user:
            self.delete(user)
            await self.commit()
        return user

class AsyncAdminUserHandler(AsyncUserHandler):
    @handle_exceptions_and_rollback
    @log_to_db
    async def create_admin_user(self, username, password, email, admin_status='regular'):
        existing_user_with_same_username = await self.get_by(User, username=username)
        if existing_user_with_same_username is not None:
            raise ValueError("A user with this username already exists")

        existing_user_with_same_email = await self.get_by(User, email=email)
        if existing_user_with_same_email is not None:
            raise ValueError("A user with this email already exists")

        admin_user = AdminUser()
        admin_user.set_username(username)
        admin_user.set_email(email)
        admin_user.admin_status = admin_status
        admin_user.set_password(password)
        await self.add(admin_user)
        await self.commit()
        return admin_user
    
    @handle_exceptions_and_rollback
    @log_to_db
    async def update_admin_user(self, user_id, **kwargs):
        user = await self.get_by(AdminUser, id=user_id)
        if user:
            for key, value in kwargs.items():
                setattr(user, key, value)
            await self.commit()
        return user
    
    @handle_exceptions_and_rollback
    @log_to_db
    async def delete_admin_user(self, user_id):
        user = await self.get_by_id(AdminUser, user_id)
        if user:
            self.delete(user)
            await self.commit()
        return user