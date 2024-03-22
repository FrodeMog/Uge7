import unittest
from db_connect import AsyncDatabaseConnect
from db_handler_async import *
from db_classes import *
from faker import Faker as fk
from db_classes import Base
from werkzeug.security import check_password_hash
from sqlalchemy import desc, func, select, text
import logging
from sqlalchemy.exc import SQLAlchemyError
import asyncio
#python -m unittest -v test_async.py

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

    def get_new_session(self):
        return self.db_connect.get_new_session()


class TestPopulateDatabase(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        cls.loop = asyncio.get_event_loop()
        cls.loop.run_until_complete(cls.asyncSetUpClass())

    @classmethod
    async def asyncSetUpClass(cls):
        cls.setup = Setup()
        await cls.setup.initialize()
        cls.session = AsyncSession(cls.setup.engine)
        await CleanDatabase(cls.session).clean()

    async def asyncSetUp(self):
        self.session = self.__class__.session

        self.setup.db_h.session = self.session
        self.setup.user_h.session = self.session
        self.setup.admin_user_h.session = self.session
        self.setup.category_h.session = self.session
        self.setup.product_h.session = self.session
        self.setup.transaction_h.session = self.session

        await self.session.flush() 

    async def asyncTearDown(self):
        await self.session.close()
        await self.setup.engine.dispose()

    async def test_invalid_email(self):
        async with self.setup.get_new_session() as session:
            self.setup.user_h.session = session
            try:
                user = await self.setup.user_h.create_user(
                    username="test_invalid_email",
                    password=self.setup.fake.password(),
                    email="invalidemail.com"
                )
            except Exception:
                pass
            queried_log = select(Log).where(Log.kwargs.contains({"test_invalid_email"}))
            result = await session.execute(queried_log)
            queried_log = result.scalars().first()
            if queried_log is not None:
                self.assertEqual(queried_log.status, "FAIL")
            else:
                self.fail("No log entry found")

    async def test_create_user(self):
        async with self.setup.get_new_session() as session:
            self.setup.user_h.session = session
            fakepassword = self.setup.fake.password()
            user = await self.setup.user_h.create_user(
                username="test_create_user",
                password=fakepassword,
                email=self.setup.fake.email()
            )
            queried_user = await self.setup.db_h.get_by(User, username="test_create_user")
            self.assertTrue(check_password_hash(queried_user.password, fakepassword))

    async def test_create_admin_user(self):
        async with self.setup.get_new_session() as session:
            self.setup.admin_user_h.session = session
            fakepassword = self.setup.fake.password()
            user = await self.setup.admin_user_h.create_admin_user(
                username="test_create_admin_user",
                password=fakepassword,
                email=self.setup.fake.email()
            )
            queried_user = await self.setup.db_h.get_by(User, username="test_create_admin_user")
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
