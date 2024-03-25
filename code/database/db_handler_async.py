import db_classes
from db_classes import *
from db_classes import ALLOWED_CURRENCIES, ALLOWED_TRANSACTION_TYPES, ALLOWED_ADMIN_STATUSES
from db_decorators_async import log_to_db
from sqlalchemy import select
from db_connect import AsyncDatabaseConnect
import inspect

class Validator:
    @staticmethod
    async def validate_user(data_dict, db_handler):
        username = data_dict.get("username")
        existing_user_with_same_username = await db_handler.get_by(User, username=username)
        if existing_user_with_same_username is not None:
            raise ValueError("A user with this username already exists")

        email = data_dict.get("email")
        existing_user_with_same_email = await db_handler.get_by(User, email=email)
        if existing_user_with_same_email is not None:
            raise ValueError("A user with this email already exists")
    
    @staticmethod
    async def validate_admin_user(data_dict, db_handler):
        await Validator.validate_user(data_dict, db_handler)
        admin_status = data_dict.get("admin_status")
        if admin_status not in ALLOWED_ADMIN_STATUSES:
            raise ValueError("Invalid admin status")
        
    @staticmethod
    async def validate_category(data_dict, db_handler):
        parent_name = data_dict.get("parent_name")
        parent_id = data_dict.get("parent_id")

        if parent_name is not None:
            parent = await db_handler.get_by(Category, name=parent_name)
            if parent is None:
                parent = Category(name=parent_name)
                await db_handler.add(parent)
        elif parent_id is not None:
            parent = await db_handler.get_by(Category, id=parent_id)
            if parent is None:
                raise ValueError(f"No category found with ID {parent_id}")
        else:
            parent = None
        return parent
        
    @staticmethod
    async def validate_product(data_dict, db_handler):
        category_name = data_dict.get("category_name")
        category_id = data_dict.get("category_id")

        if category_name is not None:
            category = await db_handler.get_by(Category, name=category_name)
            if category is None:
                raise ValueError(f"No category found with name {category_name}")
        elif category_id is not None:
            category = await db_handler.get_by(Category, id=category_id)
            if category is None:
                raise ValueError(f"No category found with ID {category_id}")
        else:
            category = await db_handler.get_by(Category, id=1)  # Use the default "Unknown" category
        return category
        
    @staticmethod
    async def validate_transaction(data_dict, db_handler):
        product_id = data_dict.get("product_id")
        product = await db_handler.get_by(Product, id=product_id)
        if product is None:
            raise ValueError(f"No product found with ID {product_id}")

        transaction_type = data_dict.get("transaction_type")
        if transaction_type not in ALLOWED_TRANSACTION_TYPES:
            raise ValueError("Invalid transaction type")
        
        currency = data_dict.get("currency").lower()
        if currency not in ALLOWED_CURRENCIES:
            raise ValueError("Invalid currency")

        quantity = data_dict.get("quantity")
        if transaction_type == 'purchase' and product.quantity < quantity:
            raise ValueError("Not enough stock for purchase")

class Service:
    def __init__(self, session, db_handler):
        self.session = session
        self.db_handler = db_handler

    @log_to_db
    async def create_user(self, username, email, password):
        data_dict = {"username": username, "email": email, "password": password}
        await Validator.validate_user(data_dict, self.db_handler)
        user = User()
        user.set_username(username)
        user.set_email(email)
        user.set_password(password)
        await self.db_handler.add(user)
        return user
    
    @log_to_db
    async def create_adminuser(self, username, email, password, admin_status):
        data_dict = {"username": username, "email": email, "password": password, "admin_status": admin_status}
        await Validator.validate_user(data_dict, self.db_handler)
        await Validator.validate_admin_user(data_dict, self.db_handler)
        user = AdminUser()
        user.set_username(username)
        user.set_email(email)
        user.set_password(password)
        user.admin_status = admin_status
        await self.db_handler.add(user)
        return user
    
    @log_to_db
    async def create_category(self, name, description=None, parent_id=None, parent_name=None):
        # Check if there are any categories in the database
        if not await self.db_handler.get_all(Category):
            # If not, create the "Unknown" category
            unknown_category = Category(name="Unknown", description="Unknown category. Reference for products with no category assigned.")
            await self.db_handler.add(unknown_category)

        data_dict = {
            "name": name,
            "description": description,
            "parent_id": parent_id,
            "parent_name": parent_name
        }
        parent = await Validator.validate_category(data_dict, self.db_handler)

        category = Category(
            name=name,
            description=description,
            parent_id=parent.id if parent else None
        )
        await self.db_handler.add(category)
        return category
    
    @log_to_db
    async def create_product(self, name, description, purchase_price, restock_price, currency, quantity, category_id=None, category_name=None):
        data_dict = {
            "name": name,
            "description": description,
            "purchase_price": purchase_price,
            "restock_price": restock_price,
            "currency": currency,
            "quantity": quantity,
            "category_id": category_id,
            "category_name": category_name
        }
        category = await Validator.validate_product(data_dict, self.db_handler)

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
        await self.db_handler.add(product)
        return product
    
    @log_to_db
    async def create_transaction(self, product_id, user_id, quantity, transaction_type, currency):
        data_dict = {
            "product_id": product_id,
            "user_id": user_id,
            "quantity": quantity,
            "transaction_type": transaction_type,
            "currency": currency
        }
        await Validator.validate_transaction(data_dict, self.db_handler)

        product = await self.db_handler.get_by(Product, id=product_id)

        if transaction_type == 'purchase':
            product.quantity -= quantity
            price = product.purchase_price * quantity
        elif transaction_type == 'refund':
            product.quantity += quantity
            price = -product.purchase_price * quantity
        elif transaction_type == 'restock':
            product.quantity += quantity
            price = -product.restock_price * quantity

        transaction = Transaction(
            product_id=product_id,
            user_id=user_id,
            price=price,
            quantity=quantity,
            transaction_type=transaction_type,
            currency=currency
        )
        await self.db_handler.add(transaction)
        return transaction
        
class AsyncDatabaseHandler():
    def __init__(self, item_type=None):
        self.db_connect = None
        self.session = None
        self.item_type = item_type.lower() if item_type else None

        # Get all classes from the db_classes module
        all_classes = [cls for name, cls in inspect.getmembers(db_classes, inspect.isclass)]

        # Create a type map from the class names to the classes
        self.type_map = {cls.__name__.lower(): cls for cls in all_classes}

        # Create a Service object with session=None and db_handler=self
        self.service = Service(None, self)

    async def connect(self):
        self.db_connect = await AsyncDatabaseConnect.connect_from_config()
        self.session = await self.db_connect.get_new_session()
        self.transaction = await self.session.begin()
        self.service.session = self.session
        await self.session.flush()

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.transaction is not None and self.transaction.is_active:
            if exc_type is not None:
                await self.transaction.rollback()
            else:
                await self.transaction.commit()
        await self.session.close()
        await self.db_connect.close()

    async def start(self):
        self.transaction = await self.session.begin()
        await self.session.flush()

    async def commit(self):
        try:
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            raise e
        
    async def rollback(self):
        await self.session.rollback()
    
    async def close(self):
        await self.session.close()
        await self.engine.dispose()

    async def create(self, **kwargs):
        item_type_lower = self.item_type.lower()
        if item_type_lower in self.type_map and hasattr(self.service, f"create_{item_type_lower}"):
            create_method = getattr(self.service, f"create_{item_type_lower}")
            return await create_method(**kwargs)
        else:
            raise ValueError(f"Invalid item type: {self.item_type}")

    async def add(self, instance):
        item_type_lower = type(instance).__name__.lower()
        if hasattr(self.service, f"add_{item_type_lower}"):
            add_method = getattr(self.service, f"add_{item_type_lower}")
            return await add_method(instance)
        else:
            self.session.add(instance)

    async def delete(self, instance):
        item_type_lower = type(instance).__name__.lower()
        if hasattr(self.service, f"delete_{item_type_lower}"):
            delete_method = getattr(self.service, f"delete_{item_type_lower}")
            return await delete_method(instance)
        else:
            self.session.delete(instance)

    async def update(self, instance, **kwargs):
        item_type_lower = type(instance).__name__.lower()
        if hasattr(self.service, f"update_{item_type_lower}"):
            update_method = getattr(self.service, f"update_{item_type_lower}")
            return await update_method(instance, **kwargs)
        else:
            self.session.query(instance).update(kwargs)

    async def get_by_contains(self, model, **filters):
        stmt = select(model).where(*[getattr(model, k).contains(v) for k, v in filters.items()])
        result = await self.session.execute(stmt)
        return result.scalars().one_or_none()

    async def get_by_id(self, model, id):
        result = await self.session.execute(select(model).filter(model.id == id))
        return result.scalars().first()

    async def get_by(self, model, **filters):
        stmt = select(model).where(*[getattr(model, k) == v for k, v in filters.items()])
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_all(self, model):
        result = await self.session.execute(select(model))
        return result.scalars().all()

    async def get_all_by(self, model, **filters):
        result = await self.session.execute(select(model).filter_by(**filters))
        return result.scalars().all()