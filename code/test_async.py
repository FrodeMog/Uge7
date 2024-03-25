import unittest
from db_handler_async import *
from db_classes import *
from faker import Faker as fk
from db_classes import Base
from werkzeug.security import check_password_hash
from sqlalchemy import desc, func, select, text
import logging
import os
#python -m unittest -v test_async.py

logging.basicConfig(level=logging.ERROR)
os.environ['PYTHONASYNCIODEBUG'] = '1'

class CleanDatabase():
    def __init__(self, session):
        self.engine = session.get_bind()
        self.session = session

    async def clean(self):
        await self.session.run_sync(self._drop_and_create_all)

    def _drop_and_create_all(self, sync_session):
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)

class TestAsyncDatabaseHandler(unittest.IsolatedAsyncioTestCase):
    
    async def test_create_category(self):
        async with AsyncDatabaseHandler("Category") as db_h:
            try:
                category = await db_h.create(name="test_create_category")
                queried_category = await db_h.get_by(Category, name="test_create_category")
            except Exception as e:
                logging.error(e)
                self.fail("Failed to create category")
        self.assertIsNotNone(queried_category)

    async def test_create_product(self):
        async with AsyncDatabaseHandler("Product") as db_h:
            try:
                product = await db_h.create(
                    name="test_create_product",
                    description="test description",
                    category_id=1,
                    purchase_price=1.0,
                    restock_price=1.0,
                    currency="USD",
                    quantity=1
                )
                queried_product = await db_h.get_by(Product, name="test_create_product")
            except Exception as e:
                logging.error(e)
                self.fail("Failed to create product")
        self.assertIsNotNone(queried_product)
    
    async def test_create_transaction(self):
        async with AsyncDatabaseHandler("Product") as db_h:
            try:
                product = await db_h.create(
                    name="test_create_transaction",
                    description="test description",
                    category_id=1,
                    purchase_price=1.0,
                    restock_price=1.0,
                    currency="USD",
                    quantity=1
                )
                query_product = await db_h.get_by(Product, name="test_create_transaction")
            except Exception as e:
                logging.error(e)
                self.fail("Failed to create product")
        async with AsyncDatabaseHandler("User") as db_h:
            try:
                user = await db_h.create(
                    username="test_create_transaction",
                    password="testpassword",
                    email="test_create_transaction@test.com"
                )
                queried_user = await db_h.get_by(User, username="test_create_transaction")
            except Exception as e:
                logging.error(e)
                self.fail("Failed to create user")
        async with AsyncDatabaseHandler("Transaction") as db_h:
            try:
                transaction = await db_h.create(
                    product_id=query_product.id,
                    user_id=queried_user.id,
                    transaction_type="purchase",
                    quantity=1,
                    currency="USD",
                )
                queried_transaction = await db_h.get_by(Transaction, product_id=query_product.id, user_id=queried_user.id)
            except Exception as e:
                logging.error(e)
                self.fail("Failed to create transaction")
        self.assertIsNotNone(queried_transaction)

    async def test_multiple_sessions(self):
        fake = fk()
        async with AsyncDatabaseHandler("User") as db_h:
            try:
                fakepassword = fake.password()
                user = await db_h.create(
                    username="test_multiple_sessions1",
                    password=fakepassword,
                    email=fake.email()
                )
            except Exception as e:
                logging.error(e)
                self.fail("Failed to create user")
        
        async with AsyncDatabaseHandler("User") as db_h:
            try:
                fakepassword = fake.password()
                user = await db_h.create(
                    username="test_multiple_sessions2",
                    password=fakepassword,
                    email=fake.email()
                )
            except Exception as e:
                logging.error(e)
                self.fail("Failed to create user")
        
        async with AsyncDatabaseHandler() as db_h:
            try:
                queried_user1 = await db_h.get_by(User, username="test_multiple_sessions1")
                queried_user2 = await db_h.get_by(User, username="test_multiple_sessions2")
            except Exception as e:
                logging.error(e)
                self.fail("Failed to query user")
            
        self.assertIsNotNone(queried_user1)
        self.assertIsNotNone(queried_user2)

    async def test_create_user(self):
        fake = fk()
        async with AsyncDatabaseHandler("User") as db_h:
            try:
                fakepassword = fake.password()
                user = await db_h.create(
                    username="test_create_user",
                    password=fakepassword,
                    email=fake.email()
                )
                queried_user = await db_h.get_by(User, username="test_create_user")
            except Exception as e:
                logging.error(e)
                self.fail("Failed to create user")
        if queried_user is not None:
            self.assertTrue(check_password_hash(queried_user.password, fakepassword))
    
    async def test_create_many_users(self):
        fake = fk()
        async with AsyncDatabaseHandler("User") as db_h:
            try:
                for _ in range(10):
                    fakepassword = fake.password()
                    user = await db_h.create(
                        username=fake.user_name(),
                        password=fakepassword,
                        email=fake.email()
                    )
                queried_users = await db_h.get_all(User)
            except Exception as e:
                logging.error(e)
                self.fail("Failed to create users")
        if queried_users is not None:
            self.assertGreaterEqual(len(queried_users), 10)

    async def test_create_admin_user(self):
        fake = fk()
        async with AsyncDatabaseHandler("AdminUser") as db_h:
            try:
                fakepassword = fake.password()
                user = await db_h.create(
                    username="test_create_admin_user",
                    password=fakepassword,
                    email=fake.email(),
                    admin_status="regular"
                )
                queried_user = await db_h.get_by(AdminUser, username="test_create_admin_user")
            except Exception as e:
                logging.error(e)
                self.fail("Failed to create admin user")
        if queried_user is not None:
            self.assertTrue(check_password_hash(queried_user.password, fakepassword))
            self.assertEqual(queried_user.admin_status, "regular")

    async def test_invalid_email(self):
        fake = fk()
        try:
            async with AsyncDatabaseHandler("User") as db_h:
                fakepassword = fake.password()
                user = await db_h.create(
                    username="test_invalid_email",
                    password=fakepassword,
                    email="invalidemail.com"
                )
        except Exception:
            pass

        async with AsyncDatabaseHandler("Log") as db_h:
            queried_log = await db_h.get_by_contains(Log, kwargs="test_invalid_email")

        if queried_log is not None:
            self.assertEqual(queried_log.status, "FAIL")
        else:
            self.fail("No log entry found")

    async def test_clean_database(self):
       async with AsyncDatabaseHandler("User") as db_h:
           cleaner = CleanDatabase(db_h.session)
           await cleaner.clean()
           result = await db_h.session.execute(select(User))
           self.assertEqual(result.scalars().all(), [])
           # No need to close the session manually, it's done automatically

class CustomTestResult(unittest.TextTestResult):
    def printErrors(self):
        self.stream.writeln("Passed: {}".format(self.testsRun - len(self.failures) - len(self.errors)))
        self.stream.writeln("Failed: {}".format(len(self.failures)))
        self.stream.writeln("Errors: {}".format(len(self.errors)))
        super().printErrors()

class CustomTestRunner(unittest.TextTestRunner):
    resultclass = CustomTestResult

def suite(): # make sure we run clean_database first
    suite = unittest.TestSuite()
    suite.addTest(TestAsyncDatabaseHandler('test_clean_database'))

    all_tests = unittest.defaultTestLoader.getTestCaseNames(TestAsyncDatabaseHandler)
    for test_name in all_tests:
        if test_name != 'test_clean_database':
            suite.addTest(TestAsyncDatabaseHandler(test_name))

    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
