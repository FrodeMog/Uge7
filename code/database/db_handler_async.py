import db_classes
from db_classes import *
from db_classes import ALLOWED_CURRENCIES, ALLOWED_TRANSACTION_TYPES, ALLOWED_ADMIN_STATUSES
from db_decorators_async import log_to_db
from sqlalchemy import select, update, and_
from db_connect import AsyncDatabaseConnect
import inspect

script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, '..', 'data', 'currencies.json')
with open(file_path, 'r') as f:
    currencies_data = json.load(f)

CURRENCY_CONVERSION_RATES = dict(currencies_data['conversion_currencies'])

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
        name = data_dict.get("name")
        existing_category_with_same_name = await db_handler.get_by(Category, name=name)
        if existing_category_with_same_name is not None:
            raise ValueError("A category with this name already exists")
        
    @staticmethod
    async def validate_product(data_dict, db_handler):

        name = data_dict.get("name")
        existing_product_with_same_name = await db_handler.get_by(Product, name=name)
        if existing_product_with_same_name is not None:
            raise ValueError("A product with this name already exists")

        category_name = data_dict.get("category_name")
        category = None

        if category_name is not None:
            category = await db_handler.get_by(Category, name=category_name)

        if category is None:
            category = await db_handler.get_by(Category, id=1)  # Use the default "Unknown" category
            if category is None:
                raise ValueError("No category found with ID 1")

        return category
    
    @staticmethod
    async def validate_update_product(product_data, db_handler, existing_product=None):
        # If the product name hasn't changed, skip the unique name check
        if existing_product is not None and existing_product.name == product_data.get('name'):
            return

        # Check if a product with the same name already exists
        existing_product_with_same_name = await db_handler.get_by(Product, name=product_data.get('name'))
        if existing_product_with_same_name is not None and existing_product_with_same_name.id != existing_product.id:
            raise ValueError("A product with this name already exists")
        
    @staticmethod
    async def validate_update_category(category_data, db_handler, existing_category=None):
        # If the category name hasn't changed, skip the unique name check
        if existing_category is not None and existing_category.name == category_data.get('name'):
            return

        # Check if a category with the same name already exists
        existing_category_with_same_name = await db_handler.get_by(Category, name=category_data.get('name'))
        if existing_category_with_same_name is not None and existing_category_with_same_name.id != existing_category.id:
            raise ValueError("A category with this name already exists")

    @staticmethod
    async def validate_transaction(data_dict, db_handler):
        product_id = data_dict.get("product_id")
        product = await db_handler.get_by(Product, id=product_id)
        if product is None:
            raise ValueError(f"No product found with ID {product_id}")

        transaction_type = data_dict.get("transaction_type")
        if transaction_type not in ALLOWED_TRANSACTION_TYPES:
            raise ValueError("Invalid transaction type")
        
        currency = data_dict.get("currency")
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

        data_dict = {"name": name, "description": description, "parent_id": parent_id, "parent_name": parent_name}
        await Validator.validate_category(data_dict, self.db_handler)

        if parent_name is not None:
            parent = await self.db_handler.get_by(Category, name=parent_name)
            if parent is None:
                parent = Category(name=parent_name)
                await self.db_handler.add(parent)
                await self.db_handler.commit()
        elif parent_id is not None:
            parent = await self.db_handler.get_by(Category, id=parent_id)
            if parent is None:
                raise ValueError(f"No category found with ID {parent_id}")
        else:
            parent = None

        category = Category(
            name=name,
            description=description,
            parent_id=parent.id if parent else None
        )
        await self.db_handler.add(category)
        return category
    
    @log_to_db
    async def create_product(self, name, description, purchase_price, restock_price, currency, quantity, category_name=None):
        data_dict = {
            "name": name,
            "description": description,
            "purchase_price": purchase_price,
            "restock_price": restock_price,
            "currency": currency,
            "quantity": quantity,
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
    async def delete_by_id_product(self, product):
        # Get the "deleted product" reference
        stmt = select(Product).where(Product.name == 'deleted_product')
        result = await self.db_handler.session.execute(stmt)
        deleted_product = result.scalars().first()

        if not deleted_product:
            # If the "deleted product" doesn't exist, create it
            deleted_product = Product(name='deleted_product', description='This is a placeholder for a deleted product', currency='USD')
            await self.db_handler.add(deleted_product)
            await self.db_handler.commit()  # Commit the transaction to save the new product

        # Update transactions that reference the product to reference the "deleted product" instead
        transactions = await self.db_handler.get_all_by(Transaction, product_id=product.id)
        for transaction in transactions:
            await self.db_handler.update(transaction, product_id=deleted_product.id)

        # Now delete the product
        await self.db_handler.delete(product)

    @log_to_db
    async def delete_by_id_category(self, category):
        # Get the "deleted category" reference
        stmt = select(Category).where(Category.name == 'deleted_category')
        result = await self.db_handler.session.execute(stmt)
        deleted_category = result.scalars().first()

        if not deleted_category:
            # If the "deleted category" doesn't exist, create it
            deleted_category = Category(name='deleted_category', description='This is a placeholder for a deleted category')
            await self.db_handler.add(deleted_category)
            await self.db_handler.commit()  # Commit the transaction to save the new category

        # Update products that reference the category to reference the "deleted category" instead
        products = await self.db_handler.get_all_by(Product, category_id=category.id)
        for product in products:
            await self.db_handler.update(product, category_id=deleted_category.id)

        # Now delete the category
        await self.db_handler.delete(category)
    
    @log_to_db
    async def delete_by_id_user(self, user):
        # Get the "deleted user" reference
        stmt = select(User).where(User.username == 'deleted_user')
        result = await self.db_handler.session.execute(stmt)
        deleted_user = result.scalars().first()

        if not deleted_user:
            # If the "deleted user" doesn't exist, create it
            deleted_user = User(username='deleted_user', email="a@a.com", password="deleted_user")
            await self.db_handler.add(deleted_user)
            await self.db_handler.commit()  # Commit the transaction to save the new user

        # Update transactions that reference the user to reference the "deleted user" instead
        transactions = await self.db_handler.get_all_by(Transaction, user_id=user.id)
        for transaction in transactions:
            await self.db_handler.update(transaction, user_id=deleted_user.id)

        # Now delete the user
        await self.db_handler.delete(user)
    
    @log_to_db
    async def update_by_id_product(self, product, **kwargs):
        # Separate category_name from the other fields
        category_name = kwargs.pop('category_name', None)

        # Validate and update the product
        await Validator.validate_update_product(kwargs, self.db_handler, existing_product=product)
        await self.db_handler.update(product, **kwargs)

        # If category_name was provided, update the product's category
        if category_name is not None:
            # Fetch the product's category and update its name
            category = await self.db_handler.get_by_id(Category, product.category_id)
            category.name = category_name
            await self.db_handler.commit()
    
    @log_to_db
    async def update_by_id_category(self, category, **kwargs):
        # Separate parent_name from the other fields
        parent_name = kwargs.pop('parent_name', None)

        # Validate and update the category
        await Validator.validate_update_category(kwargs, self.db_handler, existing_category=category)
        await self.db_handler.update(category, **kwargs)

        # If parent_name was provided, update the category's parent
        if parent_name is not None:
            # Fetch the category's parent
            parent = await self.db_handler.get_by(Category, id=category.parent_id)
            if parent is None:
                raise ValueError(f"No category found with ID {category.parent_id}")
            parent.name = parent_name
            await self.db_handler.commit()
    
    @log_to_db
    async def create_transaction(self, product_id, user_id, quantity, transaction_type, currency):
        currency = currency.lower()
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

        # Convert price to the target currency
        conversion_rate_product = CURRENCY_CONVERSION_RATES[product.currency]
        conversion_rate_transaction = CURRENCY_CONVERSION_RATES[currency]
        price_in_target_currency = price * conversion_rate_transaction / conversion_rate_product

        transaction = Transaction(
            product_id=product_id,
            user_id=user_id,
            price=price_in_target_currency,
            quantity=quantity,
            transaction_type=transaction_type,
            currency=currency
        )
        await self.db_handler.add(transaction)
        return transaction

def filter_deleted_references(model):
    conditions = []
    if hasattr(model, 'name'):
        conditions.extend([model.name != 'deleted_user', model.name != 'deleted_category', model.name != 'deleted_product'])
    if hasattr(model, 'username'):
        conditions.append(model.username != 'deleted_user')
    return and_(*conditions)

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
        print(f"exc_type: {exc_type}, exc_val: {exc_val}, exc_tb: {exc_tb}")
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
            await self.session.delete(instance)

    async def delete_by_id(self, model, id):
        instance = await self.get_by_id(model, id)
        if instance is not None:
            item_type_lower = type(instance).__name__.lower()
            if hasattr(self.service, f"delete_by_id_{item_type_lower}"):
                delete_method = getattr(self.service, f"delete_by_id_{item_type_lower}")
                return await delete_method(instance)
            else:
                await self.session.delete(instance)

    async def update(self, instance, **kwargs):
        item_type_lower = type(instance).__name__.lower()
        if hasattr(self.service, f"update_{item_type_lower}"):
            update_method = getattr(self.service, f"update_{item_type_lower}")
            return await update_method(instance, **kwargs)
        else:
            stmt = update(instance.__class__).where(instance.__class__.id == instance.id).values(**kwargs)
            await self.session.execute(stmt)
        
    async def update_by_id(self, model, id, **kwargs):
        instance = await self.get_by_id(model, id)
        if instance is not None:
            item_type_lower = type(instance).__name__.lower()
            if hasattr(self.service, f"update_by_id_{item_type_lower}"):
                update_method = getattr(self.service, f"update_by_id_{item_type_lower}")
                return await update_method(instance, **kwargs)
            else:
                stmt = update(model).where(model.id == id).values(**kwargs)
                await self.session.execute(stmt)
                await self.session.commit()

    async def get_by_contains(self, model, **filters):
        stmt = select(model).where(and_(*[getattr(model, k).contains(v) for k, v in filters.items()], filter_deleted_references(model)))
        result = await self.session.execute(stmt)
        return result.scalars().one_or_none()

    async def get_by_id(self, model, id):
        result = await self.session.execute(select(model).where(and_(model.id == id, filter_deleted_references(model))))
        return result.scalars().first()

    async def get_by(self, model, **filters):
        stmt = select(model).where(and_(*[getattr(model, k) == v for k, v in filters.items()], filter_deleted_references(model)))
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_all(self, model):
        result = await self.session.execute(select(model).where(filter_deleted_references(model)))
        return result.scalars().all()

    async def get_all_by(self, model, **filters):
        result = await self.session.execute(select(model).where(and_(*[getattr(model, k) == v for k, v in filters.items()], filter_deleted_references(model))))
        return result.scalars().all()

    async def get_all_with_condition(self, model, condition):
        result = await self.session.execute(select(model).where(and_(condition, filter_deleted_references(model))))
        return result.scalars().all()