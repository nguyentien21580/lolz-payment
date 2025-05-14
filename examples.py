"""
Примеры использования библиотеки LolzPayment
"""

import logging
import random
import time

from models import PaymentMethod
from lolz_payment import LolzPayment


def setup_logger() -> logging.Logger:
    """Настройка логгера для примеров"""
    logger = logging.getLogger("LolzPaymentExamples")
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


def example_create_payment() -> str | None:
    """Пример создания платежа"""
    # Путь к файлу с cookies
    cookies_path = "cookies/lolz.json"

    # Создание экземпляра класса для работы с платежами
    lolz = LolzPayment(cookies_path)

    # Данные для платежа
    amount = 100.0  # сумма в рублях

    # Выбор метода оплаты
    # PaymentMethod.CARD.value - карты Paymentlnk_Card (от 10р)
    # PaymentMethod.SBP.value - СБП Paymentlnk_Sbp (от 10р)
    # PaymentMethod.BINANCE.value - Бинанс Settlepay_Binance (от 100р)
    # PaymentMethod.STEAM.value - Скины Steam Ruks_SkinPay (от 500р)
    payment_method = PaymentMethod.CARD.value

    # Телефон для СБП (необязательно для других методов)
    phone = None
    if payment_method == PaymentMethod.SBP.value:
        # Для СБП нужен номер телефона
        phone = f"+7{random.randint(9000000000, 9999999999)}"

    # Создание платежа
    response = lolz.create_payment(amount, payment_method, phone)

    # Проверка результата
    if response.error:
        print(f"Ошибка при создании платежа: {response.error}")
    else:
        print("Платеж успешно создан!")
        print(f"ID платежа: {response.payment_id}")
        print(f"URL для оплаты: {response.final_url}")

        # Вернем ID платежа для использования в других примерах
        return response.payment_id

    return None


def example_check_payment(payment_id) -> bool:
    """Пример проверки статуса платежа"""
    # Путь к файлу с cookies
    cookies_path = "cookies/lolz.json"

    # Создание экземпляра класса для работы с платежами
    lolz = LolzPayment(cookies_path)

    # Проверка платежа
    payment_info = lolz.check_payment(payment_id)

    # Проверка результата
    if not payment_info:
        print(f"Не удалось получить информацию о платеже {payment_id}")
        return False

    print(f"Информация о платеже {payment_id}:")
    print(f"Дата создания: {payment_info.creation_date}")
    print(f"Статус оплаты: {payment_info.payment_date}")
    print(f"Сумма: {payment_info.amount}")
    print(f"Тип платежа: {payment_info.payment_type}")
    print(f"Оплачен: {'Да' if payment_info.is_paid else 'Нет'}")

    return payment_info.is_paid


def example_wait_for_payment(
    payment_id, timeout_seconds=300, check_interval_seconds=10
) -> bool:
    """Пример ожидания оплаты платежа"""
    # Путь к файлу с cookies
    cookies_path = "cookies/lolz.json"

    # Создание экземпляра класса для работы с платежами
    lolz = LolzPayment(cookies_path)

    print(f"Ожидание оплаты платежа {payment_id}...")
    start_time = time.time()

    while time.time() - start_time < timeout_seconds:
        # Проверка платежа
        payment_info = lolz.check_payment(payment_id)

        if not payment_info:
            print("Не удалось получить информацию о платеже")
            time.sleep(check_interval_seconds)
            continue

        if payment_info.is_paid:
            print(f"Платеж {payment_id} успешно оплачен!")
            return True

        print(f"Платеж {payment_id} еще не оплачен. Ожидание...")
        time.sleep(check_interval_seconds)

    print(f"Истекло время ожидания для платежа {payment_id}")
    return False


def example_binance_payment() -> str | None:
    """Пример создания платежа через Binance"""
    # Путь к файлу с cookies
    cookies_path = "cookies/lolz.json"

    # Создание экземпляра класса для работы с платежами
    lolz = LolzPayment(cookies_path)

    # Данные для платежа
    amount = 100.0  # минимум 100р для Binance
    payment_method = PaymentMethod.BINANCE.value

    # Создание платежа
    response = lolz.create_payment(amount, payment_method)

    # Проверка результата
    if response.error:
        print(f"Ошибка при создании платежа через Binance: {response.error}")
    else:
        print("Платеж через Binance успешно создан!")
        print(f"ID платежа: {response.payment_id}")
        print(f"URL для оплаты: {response.final_url}")

        return response.payment_id

    return None


def example_steam_payment() -> str | None:
    """Пример создания платежа через скины Steam"""
    # Путь к файлу с cookies
    cookies_path = "cookies/lolz.json"

    # Создание экземпляра класса для работы с платежами
    lolz = LolzPayment(cookies_path)

    # Данные для платежа
    amount = 500.0  # минимум 500р для Steam
    payment_method = PaymentMethod.STEAM.value

    # Создание платежа
    response = lolz.create_payment(amount, payment_method)

    # Проверка результата
    if response.error:
        print(f"Ошибка при создании платежа через Steam: {response.error}")
    else:
        print("Платеж через Steam успешно создан!")
        print(f"ID платежа: {response.payment_id}")
        print(f"URL для оплаты: {response.final_url}")

        return response.payment_id

    return None


def run_examples() -> None:
    """Запуск всех примеров"""
    print("=== Пример создания платежа через карту ===")
    payment_id = example_create_payment()

    if payment_id:
        print("\n=== Пример проверки платежа ===")
        example_check_payment(payment_id)

        print("\n=== Пример ожидания оплаты платежа ===")

        example_wait_for_payment(
            payment_id, timeout_seconds=30
        )  # 30 секунд для примера

    # Другие методы оплаты
    print("\n=== Пример создания платежа через Binance ===")
    example_binance_payment()

    print("\n=== Пример создания платежа через скины Steam ===")
    example_steam_payment()


if __name__ == "__main__":
    run_examples()
