import json
import logging
import random
import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional

from models import PaymentMethod, PaymentRequest, PaymentResponse, PaymentInfo


class LolzPayment:
    """
    Основной класс для работы с платежами Lolz Market.
    Позволяет создавать платежи и проверять их статус.
    """

    def __init__(
        self, cookies_path: str, logger: Optional[logging.Logger] = None
    ) -> None:
        """
        Инициализация клиента для работы с платежами.

        Args:
            cookies_path: Путь к файлу с cookies в формате JSON
            logger: Опциональный логгер для записи сообщений
        """
        self.cookies_path = cookies_path
        self.cookies = self._load_cookies()
        self.base_url = "https://lzt.market"
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Referer": "https://lzt.market/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        }
        self.method_mapping = {
            PaymentMethod.CARD.value: "Paymentlnk_Card",  # от 10р
            PaymentMethod.SBP.value: "Paymentlnk_Sbp",  # от 10р
            PaymentMethod.BINANCE.value: "Settlepay_Binance",  # от 100р
            PaymentMethod.STEAM.value: "Ruks_SkinPay",  # от 500р
        }

        # Минимальные суммы для методов оплаты
        self.min_amounts = {
            PaymentMethod.CARD.value: 10,
            PaymentMethod.SBP.value: 10,
            PaymentMethod.BINANCE.value: 100,
            PaymentMethod.STEAM.value: 500,
        }

        # Настройка логирования
        self.logger = logger or logging.getLogger("LolzPayment")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def _load_cookies(self) -> Dict[str, str]:
        """Загрузка cookies из файла"""
        try:
            with open(self.cookies_path, "r") as file:
                cookies_list = json.load(file)
            return {cookie["name"]: cookie["value"] for cookie in cookies_list}
        except Exception as e:
            error_msg = f"Ошибка загрузки cookies: {e}"
            print(error_msg)
            if hasattr(self, "logger"):
                self.logger.error(error_msg)
            return {}

    def _get_tokens(self) -> Optional[Dict[str, str]]:
        """Получение токенов xf_token и service_id со страницы депозита"""
        try:
            page_url = f"{self.base_url}/payment/balance/deposit"
            response = requests.get(
                page_url, headers=self.headers, cookies=self.cookies
            )

            if response.status_code != 200:
                error_msg = f"Ошибка: Получен статус код {response.status_code}"
                self.logger.error(error_msg)
                return None

            soup = BeautifulSoup(response.text, "html.parser")

            login_form = soup.find("form", {"action": "/login/login"})
            if login_form:
                error_msg = "Ошибка авторизации: Не удалось получить токены. Пользователь не авторизован (cookie устарели или недействительны)"
                self.logger.error(error_msg)
                self.logger.debug(f"Текущие cookie: {self.cookies}")
                return None

            # Ищем токены
            xf_token_elem = soup.find("input", {"name": "_xfToken"})
            service_id_elem = soup.find("input", {"name": "service_id"})

            if not xf_token_elem or not service_id_elem:
                error_msg = "Не удалось найти токены на странице. Проверьте валидность cookie или изменения в структуре сайта."
                self.logger.error(error_msg)
                return None

            xf_token = xf_token_elem["value"]
            service_id = service_id_elem["value"]

            return {"xf_token": xf_token, "service_id": service_id}
        except Exception as e:
            error_msg = f"Ошибка получения токенов: {e}"
            self.logger.error(error_msg)

            if hasattr(self, "logger") and self.logger.level <= logging.DEBUG:
                import traceback

                self.logger.debug(
                    f"Трассировка ошибки: {traceback.format_exc()}\nСтраница: {response.text}"
                )
            return None

    def create_payment(
        self, amount: float, payment_method: str, phone: Optional[str] = None
    ) -> PaymentResponse:
        """
        Создание нового платежа в системе Lolz Market.

        Args:
            amount: Сумма платежа
            payment_method: Метод оплаты ('card', 'sbp', 'binance', 'steam')
            phone: Номер телефона (обязателен для СБП)

        Returns:
            PaymentResponse: Ответ с информацией о платеже или ошибкой
        """
        try:
            # Проверка минимальной суммы
            if amount < self.min_amounts.get(payment_method, 0):
                min_amount = self.min_amounts.get(payment_method, 0)
                error_msg = f"Минимальная сумма для метода '{payment_method}' составляет {min_amount} руб."
                self.logger.error(error_msg)
                return PaymentResponse(error=error_msg)

            # Проверка наличия телефона для СБП
            if payment_method == PaymentMethod.SBP.value and not phone:
                # Если телефон не указан, генерируем случайный
                phone = f"+7{random.randint(9000000000, 9999999999)}"
                self.logger.warning(
                    f"Для СБП не указан телефон, используем случайный: {phone}"
                )

            method_enum = PaymentMethod(payment_method)

            request = PaymentRequest(amount, method_enum, phone)

            # Получение токенов для запроса
            tokens = self._get_tokens()
            if not tokens:
                return PaymentResponse(error="Не удалось получить токены для платежа")

            url = f"{self.base_url}/payment/method"
            modified_headers = self.headers.copy()
            modified_headers["Content-Type"] = "application/x-www-form-urlencoded"
            modified_headers["Accept"] = (
                "application/json, text/javascript, */*; q=0.01"
            )
            modified_headers["Referer"] = f"{self.base_url}/payment/balance/deposit"

            data = {
                "currency": "rub",
                "amount": str(request.amount),
                "method": self.method_mapping[request.payment_method.value],
                "extra[phone]": phone
                if payment_method == PaymentMethod.SBP.value and phone
                else "",
                "service_type": "refill-balance",
                "service_id": tokens["service_id"],
                "redirect": f"{self.base_url}/",
                "_xfConfirm": "1",
                "_xfToken": tokens["xf_token"],
                "_xfRequestUri": "/payment/balance/deposit",
                "_xfNoRedirect": "1",
                "_xfResponseType": "json",
            }

            response = requests.post(
                url, headers=modified_headers, cookies=self.cookies, data=data
            )

            if response.status_code != 200:
                error_msg = f"Ошибка: Получен статус код {response.status_code}"
                self.logger.error(error_msg)
                return PaymentResponse(error=error_msg)

            response_json = response.json()
            redirect_target = response_json.get("_redirectTarget")
            redirect_message = response_json.get("_redirectMessage")

            if redirect_target and redirect_message:
                payment_id = (
                    redirect_message.split("=")[-1] if redirect_message else None
                )

                self.logger.info(f"Успешно создан платеж: {payment_id}")
                return PaymentResponse(final_url=redirect_target, payment_id=payment_id)
            else:
                error_msg = "Не удалось получить информацию о платеже"
                self.logger.error(error_msg)
                return PaymentResponse(error=error_msg)

        except Exception as e:
            error_msg = f"Произошла ошибка: {str(e)}"
            self.logger.error(error_msg)
            return PaymentResponse(error=error_msg)

    def check_payment(self, payment_id: str) -> Optional[PaymentInfo]:
        """
        Проверка статуса платежа в системе Lolz Market.

        Args:
            payment_id: Идентификатор платежа для проверки

        Returns:
            Optional[PaymentInfo]: Информация о платеже или None в случае ошибки
        """
        try:
            url = f"{self.base_url}/payment/list"
            response = requests.get(url, headers=self.headers, cookies=self.cookies)

            if response.status_code != 200:
                error_msg = f"Ошибка: Получен статус код {response.status_code}"
                self.logger.error(error_msg)
                return None

            soup = BeautifulSoup(response.text, "html.parser")
            payment_row = soup.find("td", string=payment_id)

            if payment_row:
                row = payment_row.find_parent("tr")
                cells = row.find_all("td")

                status = (
                    "completed" if cells[2].text.strip() == "Оплачен" else "pending"
                )

                payment_info = PaymentInfo(
                    payment_id=cells[0].text.strip(),
                    creation_date=cells[1].text.strip(),
                    payment_date=cells[2].text.strip(),
                    amount=cells[4].text.strip(),
                    payment_type=cells[5].text.strip(),
                    status=status,
                )

                self.logger.info(f"Получена информация о платеже: {payment_id}")
                return payment_info
            else:
                self.logger.warning(f"Платеж с ID {payment_id} не найден")
                return None

        except Exception as e:
            error_msg = f"Ошибка получения информации о платеже: {e}"
            self.logger.error(error_msg)
            return None
