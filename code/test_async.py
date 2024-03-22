import unittest
from db_connect import AsyncDatabaseConnect
from db_handler_async import *
from db_classes import *
from faker import Faker as fk
from db_classes import Base
from werkzeug.security import check_password_hash
from sqlalchemy import desc
from sqlalchemy.exc import SQLAlchemyError
import asyncio
#python -m unittest test_async.py

class CleanDatabase():
    def __init__(self, session):
        self.engine = session.get_bind()
        self.session = session

    async def clean(self):
        await self.session.run_sync(self._drop_and_create_all)

    def _drop_and_create_all(self, sync_session):
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)

class Setup():
    def __init__(self):
        self.fake = fk()

    async def initialize(self):
        self.db_connect = await AsyncDatabaseConnect.connect_from_config()
        self.engine = self.db_connect.engine
        self.session = AsyncSession(self.engine)
        self.db_h = AsyncDatabaseHandler(self.session)
        self.user_h = AsyncUserHandler(self.session)
        self.admin_user_h = AsyncAdminUserHandler(self.session)
        self.category_h = AsyncCategoryHandler(self.session)
        self.product_h = AsyncProductHandler(self.session)
        self.transaction_h = AsyncTransactionHandler(self.session)

class TestPopulateDatabase(unittest.IsolatedAsyncioTestCase):
    @classmethod
    async def asyncSetUp(cls):
        cls.setup = Setup()
        await cls.setup.initialize()
        await CleanDatabase(cls.setup.session).clean()

    @classmethod
    async def asyncTearDown(cls):
        await cls.setup.session.close()
        await cls.setup.engine.dispose()  # Close the engine

    async def test_create_user(self):
        fakepassword = self.setup.fake.password()
        user = await self.setup.user_h.create_user(
            username="test_create_user",
            password=fakepassword,
            email=self.setup.fake.email()
        )
        queried_user = await self.setup.db_h.get_by(User, username="test_create_user")
        self.assertTrue(check_password_hash(queried_user.password, fakepassword))

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
