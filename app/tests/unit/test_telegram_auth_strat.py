from copy import copy
from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch, Mock

from app.core.auth_strategies import TelegramAuthStrategy, TelegramAddAccountData
from app.core.models import TelegramAccount
from app.core import exc
from .mocks import get_mock_config
from ..utils import rand_str, rand_str_or_none, rand_user, assert_user_eq, assert_tg_account_eq


class TestTelegramAuthStrategy(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.config = get_mock_config(telegram={"token_secret": "secret"})
        self.tg_account_repo = Mock()
        self.strategy = TelegramAuthStrategy(self.tg_account_repo, self.config)

    @patch("app.core.auth_strategies.telegram.decode_jwt")
    async def test_add_auth_account(self, mock_decode_jwt):
        tg_token_data = {
            "sub": rand_str(),
            "tg_username": rand_str(),
            "tg_first_name": rand_str(),
            "tg_last_name": rand_str_or_none(),
            "tg_photo_url": rand_str_or_none()
        }

        mock_decode_jwt.return_value = copy(tg_token_data)

        user = rand_user()
        tg_token = rand_str()

        result = self.strategy.add_auth_account_to_user(
            copy(user),
            TelegramAddAccountData(token=tg_token)
        )

        mock_decode_jwt.assert_called_once_with(
            tg_token,
            [
                "tg_username",
                "tg_first_name",
                "tg_last_name",
                "tg_photo_url"
            ],
            self.config.telegram.token_secret,
        )

        assert_user_eq(result, user)

        # Rename "sub" to "tg_user_id".
        tg_token_data["tg_user_id"] = tg_token_data["sub"]
        del tg_token_data["sub"]

        assert_tg_account_eq(result.telegram_account, TelegramAccount(**tg_token_data))

    @patch("app.core.auth_strategies.telegram.decode_jwt")
    async def test_add_auth_account_with_invalid_token(self, mock_decode_jwt):
        mock_decode_jwt.raiseError.side_effect = Mock(side_effect=exc.InvalidToken("JWT"))

        user = rand_user()
        tg_token = rand_str()

        with self.assertRaises(exc.InvalidAuthData):
            self.strategy.add_auth_account_to_user(user, TelegramAddAccountData(token=tg_token))

        mock_decode_jwt.assert_called_once_with(
            tg_token,
            [
                "tg_username",
                "tg_first_name",
                "tg_last_name",
                "tg_photo_url"
            ],
            self.config.telegram.token_secret,
        )
