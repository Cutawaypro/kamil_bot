import logging
import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Config:
    bot_token: str
    admin_username: str
    follow_up_delay_hours: int


def _get_int_env(var_name: str, default: int) -> int:
    value = os.getenv(var_name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        logging.warning("Invalid value for %s: %s. Falling back to %s.", var_name, value, default)
        return default


def get_config() -> Config:
    """Return configuration populated from environment variables."""
    return Config(
        bot_token=os.getenv("BOT_TOKEN", ""),
        admin_username=os.getenv("ADMIN_USERNAME", ""),
        follow_up_delay_hours=_get_int_env("FOLLOW_UP_DELAY_HOURS", 48),
    )
