from db_connect import SingletonDatabaseConnect
from db_classes import *
from sqlalchemy import update

class DatabaseHandler:
    def __init__(self):
        db_connect = SingletonDatabaseConnect()
        self.session = db_connect.get_session()

    def add(self, instance):
        self.session.add(instance)

    def delete(self, instance):
        self.session.delete(instance)

    def commit(self):
        self.session.commit()
    
    def get_by_id(self, model, id):
        return self.session.query(model).get(id)
    
    def get_by(self, model, **filters):
        return self.session.query(model).filter_by(**filters).first()

    def get_all(self, model):
        return self.session.query(model).all()
    
class CategoryHandler(DatabaseHandler):
    def create_category(self, name, description, parent_name='Unknown'):
        parent = self.get_by(Category, name=parent_name)
        if parent is None:
            parent = Category(name=parent_name)
            self.add(parent)
            self.commit()

        category = Category(
            name=name,
            description=description,
            parent_id=parent.id
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
    def create_product(self, name, description, price, currency, quantity, category_name='Unknown'):
        category = self.get_by(Category, name=category_name)
        if category is None:
            category = Category(name=category_name)
            self.add(category)
            self.commit()

        product = Product(
            name=name,
            description=description,
            category_id=category.id,
            price=price,
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
    def create_transaction(self, product_id, user_id, profit, quantity, transaction_type, currency):
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