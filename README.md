# Lolz Payment

Модуль для создания и проверки платежей через платформу lzt.market.

## Требования

- Python 3.8+
- Библиотеки: requests, beautifulsoup4

## Установка зависимостей

```bash
pip install -r requirements.txt
```

## Настройка

Создайте файл с куки в папке `cookies/lolz.json` (экспорт куки сайта из браузера)

## Поддерживаемые методы оплаты

- `card` - карты Paymentlnk_Card (от 10 руб.)
- `sbp` - СБП Paymentlnk_Sbp (от 10 руб., требуется номер телефона)
- `binance` - Бинанс Settlepay_Binance (от 100 руб.)
- `steam` - Скины стим Ruks_SkinPay (от 500 руб.)

## Использование как библиотеку

### Установка

```python
# Просто скопируйте файлы models.py и lolz_payment.py в проект
# Или используйте их как есть
```

### Создание платежа через карту

```python
from models import PaymentMethod
from lolz_payment import LolzPayment

# Создание экземпляра класса
lolz = LolzPayment(cookies_path="cookies/lolz.json")

# Создание платежа
response = lolz.create_payment(
    amount=100,
    payment_method=PaymentMethod.CARD.value
)

# Проверка результата
if response.error:
    print(f"Ошибка: {response.error}")
else:
    print(f"Платеж создан: {response.payment_id}")
    print(f"URL для оплаты: {response.final_url}")
```

### Создание платежа через СБП (требуется телефон)

```python
from models import PaymentMethod
from lolz_payment import LolzPayment

lolz = LolzPayment(cookies_path="cookies/lolz.json")

# Создание платежа через СБП с указанием телефона
response = lolz.create_payment(
    amount=100,
    payment_method=PaymentMethod.SBP.value,
    phone="+79999999999"  # Если не указать, будет сгенерирован случайный
)
```

### Проверка статуса платежа

```python
from lolz_payment import LolzPayment

lolz = LolzPayment(cookies_path="cookies/lolz.json")

# Проверка платежа
payment_info = lolz.check_payment(payment_id="your_payment_id")

if payment_info:
    print(f"Платеж {'оплачен' if payment_info.is_paid else 'не оплачен'}")
    print(f"Сумма: {payment_info.amount}")
else:
    print("Не удалось получить информацию о платеже")
```

### Ожидание оплаты платежа

```python
import time
from lolz_payment import LolzPayment

lolz = LolzPayment(cookies_path="cookies/lolz.json")
payment_id = "your_payment_id"
timeout = 3600  # таймаут в секундах (1 час)

start_time = time.time()
while time.time() - start_time < timeout:
    payment_info = lolz.check_payment(payment_id)
    if payment_info and payment_info.is_paid:
        print("Платеж успешно оплачен!")
        break
    print("Ожидание оплаты...")
    time.sleep(10)  # проверка каждые 10 секунд
```

## Запуск примеров

```bash
python examples.py
```

## Использование CLI

### Создание платежа

```bash
python lolz_cli.py create 100 --method card
python lolz_cli.py create 100 --method sbp --phone "+79001234567"
python lolz_cli.py create 100 --method binance
python lolz_cli.py create 500 --method steam
```

### Проверка платежа

```bash
python lolz_cli.py check your_payment_id
```

## Важное замечание

> [!IMPORTANT]
> Используя этот репозиторий или любой связанный с ним код, вы соглашаетесь с [юридическим уведомлением](LEGAL_NOTICE.md). Автор **не несет ответственности за использование этого репозитория и не одобряет его**, а также не несет ответственности за любые копии, форки, повторные загрузки, сделанные другими пользователями, или за что-либо еще, связанное с этим репозиторием.
