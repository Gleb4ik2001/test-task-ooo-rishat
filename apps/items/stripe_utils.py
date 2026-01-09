"""Утилиты для работы со Stripe API."""
import stripe
from typing import Tuple

from django.conf import settings


def get_stripe_keys(currency: str) -> Tuple[str, str]:
    """
    Возвращает Stripe ключи в зависимости от валюты.

    Args:
        currency: Валюта ('usd' или 'kzt')

    Returns:
        Кортеж из (secret_key, public_key) для указанной валюты.
        По умолчанию возвращает USD ключи.

    Example:
        >>> secret, public = get_stripe_keys('usd')
        >>> secret, public = get_stripe_keys('kzt')
    """
    currency_lower = currency.lower()

    if currency_lower == 'kzt':
        return (
            settings.STRIPE_SECRET_KEY_KZT,
            settings.STRIPE_PUBLIC_KEY_KZT
        )
    else:
        # По умолчанию USD
        return (
            settings.STRIPE_SECRET_KEY,
            settings.STRIPE_PUBLIC_KEY
        )


def get_stripe_client(currency: str) -> stripe:
    """
    Возвращает настроенный Stripe клиент для указанной валюты.

    Настраивает API ключ Stripe в зависимости от валюты.
    Это позволяет использовать разные Stripe аккаунты
    для разных валют.

    Args:
        currency: Валюта ('usd' или 'kzt')

    Returns:
        Настроенный модуль stripe с установленным API ключом.

    Example:
        >>> stripe_client = get_stripe_client('usd')
        >>> session = stripe_client.checkout.Session.create(...)
    """
    secret_key, _ = get_stripe_keys(currency)
    stripe.api_key = secret_key
    return stripe

