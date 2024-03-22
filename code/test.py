import unittest
from db_connect import SingletonDatabaseConnect
from db_handler import *
from db_classes import *
from faker import Faker as fk
from db_classes import Base
from werkzeug.security import check_password_hash
from sqlalchemy import desc
from sqlalchemy.exc import SQLAlchemyError
#python -m unittest test.py

class CleanDatabase():
    def __init__(self, session):
        self.engine = session.get_bind()
        self.session = session

    def clean(self):
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)

class Setup():
    def __init__(self):
        self.session = SingletonDatabaseConnect.connect_from_config().get_session()
        self.db_h = DatabaseHandler(self.session)
        self.user_h = UserHandler(self.session)
        self.admin_user_h = AdminUserHandler(self.session)
        self.category_h = CategoryHandler(self.session)
        self.product_h = ProductHandler(self.session)
        self.transaction_h = TransactionHandler(self.session)
        self.fake = fk()

class TestPopulateDatabase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.setup = Setup()
        CleanDatabase(cls.setup.session).clean()

    def test_invalid_email(self):
        try:
            user = self.setup.user_h.create_user(
                username="test_unknown_error",
                password=self.setup.fake.password(),
                email="invalidemail.com"
            )
        except (ValueError, SQLAlchemyError):
            pass
        latest_log = self.setup.db_h.session.query(Log).order_by(desc(Log.id)).first()
        self.assertIsNotNone(latest_log)
        self.assertIsNotNone(latest_log.message)
        self.assertTrue('FAIL' in latest_log.status)
        self.assertTrue('Invalid email' in latest_log.message)

    def test_not_real_admin_status(self):
        try:
            admin_user = self.setup.admin_user_h.create_admin_user(
            username="test_unknown_error",
            password=self.setup.fake.password(),
            email="validd@email.com",
            admin_status="not_real_status"
            )
        except (ValueError, SQLAlchemyError):
            pass
        latest_log = self.setup.db_h.session.query(Log).order_by(desc(Log.id)).first()
        self.assertIsNotNone(latest_log)
        self.assertIsNotNone(latest_log.message)
        self.assertTrue('FAIL' in latest_log.status)
        self.assertTrue('Invalid admin status' in latest_log.message)

    def test_user_already_exists(self):
        try:
            user = self.setup.user_h.create_user(
                username="same_name",
                password=self.setup.fake.password(),
                email="valid@email.com"
            )
            user = self.setup.user_h.create_user(
                username="same_name",
                password=self.setup.fake.password(),
                email="validtest@email.com"
            )
        except (ValueError, SQLAlchemyError):
            pass
        latest_log = self.setup.db_h.session.query(Log).order_by(desc(Log.id)).first()
        self.assertIsNotNone(latest_log)
        self.assertIsNotNone(latest_log.message)
        self.assertTrue('FAIL' in latest_log.status)
        self.assertTrue('A user with this username already exists' in latest_log.message)

    def test_user_email_already_exists(self):
        try:
            user = self.setup.user_h.create_user(
                username="same_email",
                password=self.setup.fake.password(),
                email="same_email@email.com"
            )
            admin_user = self.setup.admin_user_h.create_admin_user(
                username="admin_same_email",
                password=self.setup.fake.password(),
                email="same_email@email.com"
            )
        except (ValueError, SQLAlchemyError):
            pass
        latest_log = self.setup.db_h.session.query(Log).order_by(desc(Log.id)).first()
        self.assertIsNotNone(latest_log)
        self.assertIsNotNone(latest_log.message)
        self.assertTrue('FAIL' in latest_log.status)
        self.assertTrue('A user with this email already exists' in latest_log.message)
    
    def test_sql_injection(self):
        try:
            user = self.setup.user_h.create_user(
                username="test_sql_injection; DROP TABLE users;",
                password=self.setup.fake.password(),
                email="test@email.com"
            )
        except (ValueError, SQLAlchemyError):
            pass
        users = self.setup.db_h.session.query(User).all()
        self.assertTrue(len(users) > 0)
    
    def test_long_category_name(self):
        try:
            category = self.setup.category_h.create_category(
                name="a" * 51,
                description=self.setup.fake.sentence()
            )
        except (ValueError, SQLAlchemyError):
            pass
        latest_log = self.setup.db_h.session.query(Log).order_by(desc(Log.id)).first()
        self.assertIsNotNone(latest_log)
        self.assertIsNotNone(latest_log.message)
        self.assertTrue('FAIL' in latest_log.status)

    def test_purchase_product_without_stock(self):
        user = self.setup.user_h.create_user(
                            username="test_purchase_product_without_stock",
                            password=self.setup.fake.password(),
                            email=self.setup.fake.email()
                            )
        product = self.setup.product_h.create_product(
                            name="test_purchase_product_without_stock",
                            description=self.setup.fake.sentence(),
                            purchase_price=100,
                            restock_price=50,
                            quantity=10,
                            currency='USD',
                            )
        with self.assertRaises(ValueError):
            self.setup.transaction_h.create_transaction(
                            product_id=product.id,
                            user_id=user.id,
                            quantity=15,
                            transaction_type='purchase',
                            currency='USD'
                            )

    def test_create_admin_users(self):
        fakepassword = self.setup.fake.password()
        admin = self.setup.admin_user_h.create_admin_user(
                            username="test_create_admin_users",
                            password=fakepassword,
                            email=self.setup.fake.email(),
                            admin_status='full'
                            )
        self.assertIsInstance(admin, AdminUser)
        self.assertTrue(check_password_hash(admin.password, fakepassword))
    
    def test_create_users(self):
        fakepassword = self.setup.fake.password()
        user = self.setup.user_h.create_user(
                            username="test_create_users",
                            password=fakepassword,
                            email=self.setup.fake.email()
                            )
        self.assertIsInstance(user, User)
        self.assertTrue(check_password_hash(user.password, fakepassword))
    
    def test_create_categories(self):
        category = self.setup.category_h.create_category(
                            name="test_create_categories",
                            description=self.setup.fake.sentence()
                            )
        self.assertIsInstance(category, Category)
    
    def test_create_categories_with_parent(self): #subcategories
        parent = self.setup.category_h.create_category(
                            name="test_create_categories_with_parent_the_parent",
                            description=self.setup.fake.sentence()
                            )
        category = self.setup.category_h.create_category(
                            name="test_create_categories_with_parent_the_child",
                            description=self.setup.fake.sentence(),
                            parent_id=parent.id
                            )
        self.assertIsInstance(category, Category)
        self.assertEqual(category.parent_id, parent.id)
        self.assertEqual(category.parent.name, parent.name)
    
    def test_create_products(self):
        category = self.setup.category_h.create_category(
                            name="test_create_products",
                            description=self.setup.fake.sentence()
                            )
        product = self.setup.product_h.create_product(
                            name="test_create_products",
                            description=self.setup.fake.sentence(),
                            purchase_price=self.setup.fake.random_number(),
                            restock_price=self.setup.fake.random_number(),
                            quantity=self.setup.fake.random_number(),
                            currency='USD',
                            category_name=category.name
                            )
        self.assertIsInstance(product, Product)
        self.assertEqual(product.category_id, category.id)
        self.assertEqual(product.category.name, category.name)
    
    def test_create_products_without_category(self):
        product = self.setup.product_h.create_product(
                            name="test_create_products_without_category",
                            description=self.setup.fake.sentence(),
                            purchase_price=self.setup.fake.random_number(),
                            restock_price=self.setup.fake.random_number(),
                            quantity=self.setup.fake.random_number(),
                            currency='USD',
                            )
        self.assertIsInstance(product, Product)
        self.assertEqual(product.category_id, 1)
        self.assertEqual(product.category.name, 'Unknown')
    
    def test_create_products_with_category_id(self):
        category = self.setup.category_h.create_category(
                            name="test_create_products_with_category_id",
                            description=self.setup.fake.sentence()
                            )
        product = self.setup.product_h.create_product(
                            name="test_create_products_with_category_id",
                            description=self.setup.fake.sentence(),
                            purchase_price=self.setup.fake.random_number(),
                            restock_price=self.setup.fake.random_number(),
                            quantity=self.setup.fake.random_number(),
                            currency='USD',
                            category_id=category.id
                            )
        self.assertIsInstance(product, Product)
        self.assertEqual(product.category_id, category.id)
        self.assertEqual(product.category.name, category.name)
    
    def test_create_product_with_new_category(self):
        product = self.setup.product_h.create_product(
                            name="test_create_product_with_new_category",
                            description=self.setup.fake.sentence(),
                            purchase_price=self.setup.fake.random_number(),
                            restock_price=self.setup.fake.random_number(),
                            quantity=self.setup.fake.random_number(),
                            currency='USD',
                            category_name="test_create_product_with_new_category"
                            )
        self.assertIsInstance(product, Product)
        self.assertEqual(product.category.name, "test_create_product_with_new_category")
    
    def test_create_product_with_subcategory(self):
        parent = self.setup.category_h.create_category(
                            name="test_create_product_with_subcategory_the_parent",
                            description=self.setup.fake.sentence()
                            )
        child = self.setup.category_h.create_category(
                            name="test_create_product_with_subcategory_the_child",
                            description=self.setup.fake.sentence(),
                            parent_id=parent.id
                            )
        product = self.setup.product_h.create_product(
                            name="test_create_product_with_subcategory",
                            description=self.setup.fake.sentence(),
                            purchase_price=self.setup.fake.random_number(),
                            restock_price=self.setup.fake.random_number(),
                            quantity=self.setup.fake.random_number(),
                            currency='USD',
                            category_name=child.name
                            )
        self.assertIsInstance(product, Product)
        self.assertEqual(product.category.parent.name, parent.name)

    def test_create_transactions_purchase(self):
        user = self.setup.user_h.create_user(
                            username="test_create_transactions_purchase",
                            password=self.setup.fake.password(),
                            email=self.setup.fake.email()
                            )
        category = self.setup.category_h.create_category(
                            name="test_create_transactions_purchase",
                            description=self.setup.fake.sentence()
                            )
        product = self.setup.product_h.create_product(
                            name="test_create_transactions_purchase",
                            description=self.setup.fake.sentence(),
                            purchase_price=100,
                            restock_price=50,
                            quantity=10,
                            currency='USD',
                            category_name=category.name
                            )
        transaction = self.setup.transaction_h.create_transaction(
                            product_id=product.id,
                            user_id=user.id,
                            quantity=5,
                            transaction_type='purchase',
                            currency='USD'
                            )
        self.assertIsInstance(transaction, Transaction)
        self.assertEqual(transaction.product_id, product.id)
        self.assertEqual(transaction.user_id, user.id)
        self.assertEqual(transaction.price, 500)
        self.assertEqual(transaction.quantity, 5)
    
    def test_create_transactions_refund(self):
        user = self.setup.user_h.create_user(
                            username="test_create_transactions_refund",
                            password=self.setup.fake.password(),
                            email=self.setup.fake.email()
                            )
        category = self.setup.category_h.create_category(
                            name="test_create_transactions_refund",
                            description=self.setup.fake.sentence()
                            )
        product = self.setup.product_h.create_product(
                            name="test_create_transactions_refund",
                            description=self.setup.fake.sentence(),
                            purchase_price=100,
                            restock_price=50,
                            quantity=10,
                            currency='USD',
                            category_name=category.name
                            )
        transaction = self.setup.transaction_h.create_transaction(
                            product_id=product.id,
                            user_id=user.id,
                            quantity=5,
                            transaction_type='refund',
                            currency='USD'
                            )
        self.assertIsInstance(transaction, Transaction)
        self.assertEqual(transaction.product_id, product.id)
        self.assertEqual(transaction.user_id, user.id)
        self.assertEqual(transaction.price, -500)
        self.assertEqual(transaction.quantity, 5)
        self.assertEqual(product.quantity, 15)

    def test_create_transactions_restock(self):
        user = self.setup.user_h.create_user(
                            username="test_create_transactions_restock",
                            password=self.setup.fake.password(),
                            email=self.setup.fake.email()
                            )
        category = self.setup.category_h.create_category(
                            name="test_create_transactions_restock",
                            description=self.setup.fake.sentence()
                            )
        product = self.setup.product_h.create_product(
                            name="test_create_transactions_restock",
                            description=self.setup.fake.sentence(),
                            purchase_price=100,
                            restock_price=50,
                            quantity=10,
                            currency='USD',
                            category_name=category.name
                            )
        transaction = self.setup.transaction_h.create_transaction(
                            product_id=product.id,
                            user_id=user.id,
                            quantity=5,
                            transaction_type='restock',
                            currency='USD'
                            )
        self.assertIsInstance(transaction, Transaction)
        self.assertEqual(transaction.product_id, product.id)
        self.assertEqual(transaction.user_id, user.id)
        self.assertEqual(transaction.price, -250)
        self.assertEqual(transaction.quantity, 5)
        self.assertEqual(product.quantity, 15)
    
    def test_create_transaction_all_scenarios(self):
        user = self.setup.user_h.create_user(
                            username="test_create_transaction_all_scenarios",
                            password=self.setup.fake.password(),
                            email=self.setup.fake.email()
                            )
        category = self.setup.category_h.create_category(
                            name="test_create_transaction_all_scenarios",
                            description=self.setup.fake.sentence()
                            )
        product = self.setup.product_h.create_product(
                            name="test_create_transaction_all_scenarios",
                            description=self.setup.fake.sentence(),
                            purchase_price=100,
                            restock_price=50,
                            quantity=10,
                            currency='USD',
                            category_name=category.name
                            )
        transaction = self.setup.transaction_h.create_transaction(
                            product_id=product.id,
                            user_id=user.id,
                            quantity=5,
                            transaction_type='purchase',
                            currency='USD'
                            )
        self.assertIsInstance(transaction, Transaction)
        self.assertEqual(transaction.product_id, product.id)
        self.assertEqual(transaction.user_id, user.id)
        self.assertEqual(transaction.price, 500)
        self.assertEqual(product.quantity, 5) # purchase 5 form 10 = 5
        transaction = self.setup.transaction_h.create_transaction(
                            product_id=product.id,
                            user_id=user.id,
                            quantity=5,
                            transaction_type='refund',
                            currency='USD'
                            )
        self.assertIsInstance(transaction, Transaction)
        self.assertEqual(transaction.product_id, product.id)
        self.assertEqual(transaction.user_id, user.id)
        self.assertEqual(transaction.price, -500)
        self.assertEqual(product.quantity, 10) # refund 5 from 5 = 10
        transaction = self.setup.transaction_h.create_transaction(
                            product_id=product.id,
                            user_id=user.id,
                            quantity=5,
                            transaction_type='restock',
                            currency='USD'
                            )
        self.assertIsInstance(transaction, Transaction)
        self.assertEqual(transaction.product_id, product.id)
        self.assertEqual(transaction.user_id, user.id)
        self.assertEqual(transaction.price, -250)
        self.assertEqual(transaction.quantity, 5)
        self.assertEqual(product.quantity, 15) # restock 5 from 10 = 15

class CustomTestResult(unittest.TextTestResult):
    def printErrors(self):
        self.stream.writeln("Passed: {}".format(self.testsRun - len(self.failures) - len(self.errors)))
        self.stream.writeln("Failed: {}".format(len(self.failures)))
        self.stream.writeln("Errors: {}".format(len(self.errors)))
        super().printErrors()

class CustomTestRunner(unittest.TextTestRunner):
    resultclass = CustomTestResult

if __name__ == '__main__':
    unittest.main(testRunner=CustomTestRunner())
