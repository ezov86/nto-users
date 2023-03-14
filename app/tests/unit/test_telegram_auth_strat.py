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

        # Patches.
        # self.decode_jwt = patch("app.core.auth_strategies.telegram.decode_jwt").start()

    async def asyncTearDown(self):
        patch.stopall()

    def assert_decode_jwt_called_once(self, mock, token: str):
        mock.assert_called_once_with(
            token,
            [
                "tg_username",
                "tg_first_name",
                "tg_last_name",
                "tg_photo_url"
            ],
            self.config.telegram.token_secret,
        )

    @patch("app.core.auth_strategies.telegram.decode_jwt")
    async def test_add_auth_account(self, decode_jwt):
        decode_jwt.return_value = self.token_data

        user = self.faker.user_model()
        token = self.faker.pystr()

        result = self.strategy.add_auth_account_to_user(
            copy(user),
            TelegramAddAccountData(token=token)
        )

        self.assert_decode_jwt_called_once(decode_jwt, token)
        assert_user_eq(result, user)
        assert_tg_account_eq(result.telegram_account, TelegramAccount(**account_data))

    @patch("app.core.auth_strategies.telegram.decode_jwt")
    async def test_add_auth_account_invalid_token(self, decode_jwt):
        decode_jwt.raiseError.side_effect = Mock(side_effect=exc.InvalidToken("JWT"))

        user = self.faker.user_model()
        token = self.faker.pystr()

        with self.assertRaises(exc.InvalidAuthData):
            self.strategy.add_auth_account_to_user(user, TelegramAddAccountData(token=token))

        self.assert_decode_jwt_called_once(decode_jwt, token)

    @patch("app.core.auth_strategies.telegram.decode_jwt")
    async def test_login_for_user_with_invalid_token(self, decode_jwt):
        decode_jwt.raiseError.side_effect = Mock(side_effect=exc.InvalidToken("JWT"))

        token = self.faker.pystr()

        with self.assertRaises(exc.InvalidAuthData):
            await self.strategy.login_for_user(TelegramLoginCredentials(token=token))

        self.assert_decode_jwt_called_once(decode_jwt, token)

