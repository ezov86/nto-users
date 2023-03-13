import unittest
from datetime import datetime
from unittest.mock import Mock

from app.core.auth_strategies import AddAuthMethodDataType, AuthStrategy
from app.core.models import User
from app.core.register import RegistrationService
from app.tests.utils import rand_str, assert_user_eq


class TestRegistrationService(unittest.TestCase):
    def startUp(self):
        self.config = Mock()
        self.config.user_default.scopes = [rand_str(), rand_str()]
        self.user_repo = Mock()
        self.strategy = Mock(spec=AuthStrategy)

        self.reg = RegistrationService(
            self.config,
            self.user_repo
        )

    async def test_valid_register(self):
        auth_data = Mock(spec=AddAuthMethodDataType)
        auth_data.name = rand_str()

        user = await self.reg.register(self.strategy, auth_data)

        self.strategy.add_auth_method_to_user.assert_called_once()
        self.user_repo.create.assert_called_once()

        assert_user_eq(
            user,
            User(
                name=auth_data.name,
                is_disabled=False,
                scopes=self.config.user_default.scopes,
                registered_at=datetime.utcnow()
            )
        )

    def test_something(self):
        self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':
    unittest.main()
