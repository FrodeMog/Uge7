import unittest
from db_connect import SingletonDatabaseConnect
from db_handler import *
from db_classes import *
from faker import Faker as fk
from db_classes import Base
from werkzeug.security import generate_password_hash, check_password_hash
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
        with open('../data/secrets.json', 'r') as f:
            secrets = json.load(f)
        username = secrets['username']
        password = secrets['password']
        database_name = secrets['test_db_name']  
        hostname = secrets['hostname']
        db_url = f"mysql+pymysql://{username}:{password}@{hostname}/{database_name}"
        self.db_connect = SingletonDatabaseConnect(db_url)
        self.session = self.db_connect.get_session()
        self.db_h = DatabaseHandler(self.session)
        self.user_h = UserHandler(self.session)
        self.admin_user_h = AdminUserHandler(self.session)
        self.category_h = CategoryHandler(self.session)
        self.product_h = ProductHandler(self.session)
        self.transaction_h = TransactionHandler(self.session)
        self.fake = fk()
        Base.metadata.create_all(self.db_connect.get_engine())

class TestPopulateDatabase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.setup = Setup()
        CleanDatabase(cls.setup.session).clean()

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
                            price=self.setup.fake.random_number(),
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
                            price=self.setup.fake.random_number(),
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
                            price=self.setup.fake.random_number(),
                            quantity=self.setup.fake.random_number(),
                            currency='USD',
                            category_id=category.id
                            )
        self.assertIsInstance(product, Product)
        self.assertEqual(product.category_id, category.id)
        self.assertEqual(product.category.name, category.name)

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
