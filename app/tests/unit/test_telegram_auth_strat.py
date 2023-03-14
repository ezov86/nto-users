from copy import copy
from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch, Mock

from app.core import exc
from app.core.auth_strategies import TelegramAuthStrategy, TelegramAddAccountData, TelegramLoginCredentials
from app.core.models import TelegramAccount
from .mocks import get_mock_config
from ..fake import get_faker
from ..utils import assert_user_eq, assert_tg_account_eq, tg_token_payload_from_data


class TestTelegramAuthStrategy(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.faker = get_faker()

        # Mocks.
        self.config = get_mock_config(telegram={"token_secret": self.faker.pystr()})
        self.tg_account_repo = Mock()

        # Strategy.
        self.strategy = TelegramAuthStrategy(self.tg_account_repo, self.config)

        # Fake data.
        self.account_data = self.faker.tg_account_data()
        self.token_data = tg_token_payload_from_data(copy(self.account_data))
        self.token = self.faker.pystr()
        self.user = self.faker.user_model()

        # Patches.
        self.decode_jwt = patch("app.core.auth_strategies.telegram.decode_jwt").start()

    async def asyncTearDown(self):
        patch.stopall()

    def set_decode_jwt_patch_normal(self):
        self.decode_jwt.return_value = self.token_data

    def set_decode_jwt_patch_raises(self):
        self.decode_jwt.raiseError.side_effect = Mock(side_effect=exc.InvalidToken("JWT"))

    def assert_decode_jwt_called_once(self, token: str):
        self.decode_jwt.assert_called_once_with(
            token,
            [
                "tg_username",
                "tg_first_name",
                "tg_last_name",
                "tg_photo_url"
            ],
            self.config.telegram.token_secret,
        )

    async def test_add_auth_account(self):
        self.set_decode_jwt_patch_normal()

        result = self.strategy.add_auth_account_to_user(
            copy(self.user),
            TelegramAddAccountData(token=self.token)
        )

        self.assert_decode_jwt_called_once(self.token)
        assert_user_eq(result, self.user)
        assert_tg_account_eq(result.telegram_account, TelegramAccount(**self.account_data))

    async def test_add_auth_account_invalid_token(self):
        self.set_decode_jwt_patch_raises()

        with self.assertRaises(exc.InvalidAuthData):
            self.strategy.add_auth_account_to_user(
                self.user,
                TelegramAddAccountData(token=self.token)
            )

        self.assert_decode_jwt_called_once(self.token)

    async def test_login_for_user_with_invalid_token(self):
        self.set_decode_jwt_patch_raises()

        with self.assertRaises(exc.InvalidAuthData):
            await self.strategy.login_for_user(TelegramLoginCredentials(token=self.token))

        self.assert_decode_jwt_called_once(self.token)
