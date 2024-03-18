from db_classes import *

class DatabaseHandler:
    def __init__(self, session):
        self.session = session

    def add(self, instance):
        self.session.add(instance)

    def delete(self, instance):
        self.session.delete(instance)

    def update(self, instance, **kwargs):
        self.session.query(instance).update(kwargs)

    def commit(self):
        self.session.commit()
    
    def get_by_id(self, model, id):
        return self.session.query(model).get(id)
    
    def get_by(self, model, **filters):
        return self.session.query(model).filter_by(**filters).first()

    def get_all(self, model):
        return self.session.query(model).all()
    
class CategoryHandler(DatabaseHandler):
    def create_category(self, name, description, parent_id=None, parent_name=None):
        # Check if there are any categories in the database
        if not self.get_all(Category):
            # If not, create the "Unknown" category
            unknown_category = Category(name="Unknown", description="Unknown category. Reference for products with no category assigned.")
            self.add(unknown_category)
            self.commit()

        parent = None
        if parent_id is not None:
            parent = self.get_by(Category, id=parent_id)
            if parent is None:
                raise ValueError(f"No category found with ID {parent_id}")
        elif parent_name is not None:
            parent = self.get_by(Category, name=parent_name)
            if parent is None:
                parent = Category(name=parent_name)
                self.add(parent)
                self.commit()

        category = Category(
            name=name,
            description=description,
            parent_id=parent.id if parent else None
        )
        self.add(category)
        self.commit()
        return category
    
    def update_category(self, category_id, **kwargs):
        category = self.get_by(Category, id=category_id)
        if category:
            for key, value in kwargs.items():
                setattr(category, key, value)
            self.commit()
        return category
    
    def delete_category(self, category_id):
        category = self.get_by_id(Category, category_id)
        if category:
            self.delete(category)
            self.commit()
        return category

class ProductHandler(DatabaseHandler):
    def create_product(self, name, description, purchase_price, restock_price, currency, quantity, category_id=None, category_name=None):
        if category_name is not None:
            category = self.get_by(Category, name=category_name)
            if category is None:
                category = Category(name=category_name)
                self.add(category)
                self.commit()
        elif category_id is not None:
            category = self.get_by(Category, id=category_id)
            if category is None:
                raise ValueError(f"No category found with ID {category_id}")
        else:
            category = self.get_by(Category, id=1)  # Use the default "Unknown" category

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
        self.add(product)
        self.commit()
        return product

    def update_product(self, product_id, **kwargs):
        product = self.get_by(Product, id=product_id)
        if product:
            for key, value in kwargs.items():
                setattr(product, key, value)
            product.changed_date = datetime.now()
            self.commit()
        return product
    
    def delete_product(self, product_id):
        product = self.get_by_id(Product, product_id)
        if product:
            self.delete(product)
            self.commit()
        return product
    
class TransactionHandler(DatabaseHandler):
    def create_transaction(self, product_id, user_id, quantity, transaction_type, currency):
        product = self.get_by(Product, id=product_id)
        if product is None:
            raise ValueError(f"No product found with ID {product_id}")

        if transaction_type == 'purchase':
            if product.quantity < quantity:
                raise ValueError("Not enough stock for purchase")
            product.quantity -= quantity
            profit = product.purchase_price * quantity
        elif transaction_type == 'refund':
            product.quantity += quantity
            profit = -product.purchase_price * quantity
        elif transaction_type == 'restock':
            product.quantity += quantity
            profit = -product.restock_price * quantity
        else:
            raise ValueError("Invalid transaction type")

        transaction = Transaction(
            product_id=product_id,
            user_id=user_id,
            profit=profit,
            quantity=quantity,
            transaction_type=transaction_type,
            currency=currency
        )
        self.add(transaction)
        self.commit()
        return transaction

class UserHandler(DatabaseHandler):
    def create_user(self, username, password, email):
        user = User(
            username=username,
            email=email
        )
        user.set_password(password)
        self.add(user)
        self.commit()
        return user
    
    def update_user(self, user_id, **kwargs):
        user = self.get_by(User, id=user_id)
        if user:
            for key, value in kwargs.items():
                setattr(user, key, value)
            self.commit()
        return user
    
    def delete_user(self, user_id):
        user = self.get_by_id(User, user_id)
        if user:
            self.delete(user)
            self.commit()
        return user

class AdminUserHandler(UserHandler):
    def create_admin_user(self, username, password, email, admin_status='regular'):
        admin_user = AdminUser(
            username=username,
            email=email,
            admin_status=admin_status
        )
        admin_user.set_password(password)
        self.add(admin_user)
        self.commit()
        return admin_user
    
    def update_admin_user(self, user_id, **kwargs):
        user = self.get_by(AdminUser, id=user_id)
        if user:
            for key, value in kwargs.items():
                setattr(user, key, value)
            self.commit()
        return user
    
    def delete_admin_user(self, user_id):
        user = self.get_by_id(AdminUser, user_id)
        if user:
            self.delete(user)
            self.commit()
        return user