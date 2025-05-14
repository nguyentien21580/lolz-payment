#!/usr/bin/env python
"""
Скрипт для быстрого создания или проверки платежа в Lolz Market.
"""

import argparse
import logging
import random
import sys
from typing import Literal

from models import PaymentMethod
from lolz_payment import LolzPayment


def setup_logging():
    """Настройка логирования"""
    logger = logging.getLogger("LolzPaymentCLI")
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


def create_payment(args) -> Literal[1] | Literal[0]:
    """Создание нового платежа"""
    logger = setup_logging()

    lolz = LolzPayment(args.cookies, logger)

    phone = args.phone
    if args.method == PaymentMethod.SBP.value and not phone:
        phone = f"+7{random.randint(9000000000, 9999999999)}"
        print(f"Для СБП не указан телефон, используем случайный: {phone}")

    response = lolz.create_payment(
        amount=args.amount, payment_method=args.method, phone=phone
    )

    if response.error:
        print(f"Ошибка при создании платежа: {response.error}")
        return 1

    print("Платеж успешно создан!")
    print(f"ID платежа: {response.payment_id}")
    print(f"URL для оплаты: {response.final_url}")
    return 0


def check_payment(args) -> Literal[1] | Literal[0]:
    """Проверка статуса платежа"""
    logger = setup_logging()

    lolz = LolzPayment(args.cookies, logger)

    payment_info = lolz.check_payment(args.id)

    if not payment_info:
        print(f"Не удалось получить информацию о платеже {args.id}")
        return 1

    print(f"Информация о платеже {args.id}:")
    print(f"Дата создания: {payment_info.creation_date}")
    print(f"Статус оплаты: {payment_info.payment_date}")
    print(f"Сумма: {payment_info.amount}")
    print(f"Тип платежа: {payment_info.payment_type}")
    print(f"Оплачен: {'Да' if payment_info.is_paid else 'Нет'}")
    return 0


def main() -> Literal[1] | Literal[0]:
    """Основная функция"""
    parser = argparse.ArgumentParser(description="Работа с платежами Lolz Market")
    parser.add_argument(
        "--cookies",
        type=str,
        default="cookies/lolz.json",
        help="Путь к файлу с cookies (по умолчанию: cookies/lolz.json)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Команда для выполнения")

    create_parser = subparsers.add_parser("create", help="Создать новый платеж")
    create_parser.add_argument("amount", type=float, help="Сумма платежа")
    create_parser.add_argument(
        "--method",
        type=str,
        choices=["card", "sbp", "binance", "steam"],
        default="card",
        help="Метод оплаты (card, sbp, binance, steam)",
    )
    create_parser.add_argument(
        "--phone", type=str, help="Номер телефона (обязателен для СБП)"
    )

    check_parser = subparsers.add_parser("check", help="Проверить статус платежа")
    check_parser.add_argument("id", type=str, help="ID платежа для проверки")

    args = parser.parse_args()

    if args.command == "create":
        return create_payment(args)
    elif args.command == "check":
        return check_payment(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
