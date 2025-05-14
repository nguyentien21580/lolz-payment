from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any


class PaymentMethod(Enum):
    CARD = "card"  # Paymentlnk_Card (от 10р)
    SBP = "sbp"  # Paymentlnk_Sbp (от 10р)
    BINANCE = "binance"  # Settlepay_Binance (от 100р)
    STEAM = "steam"  # Ruks_SkinPay (от 500р)


@dataclass
class PaymentRequest:
    amount: float
    payment_method: PaymentMethod
    phone: Optional[str] = None  # Требуется для СБП

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "amount": self.amount,
            "payment_method": self.payment_method.value,
        }
        if self.phone and self.payment_method == PaymentMethod.SBP:
            result["extra"] = {"phone": self.phone}
        return result


@dataclass
class PaymentResponse:
    final_url: Optional[str] = None
    payment_id: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {}
        if self.final_url:
            result["final_url"] = self.final_url
        if self.payment_id:
            result["payment_id"] = self.payment_id
        if self.error:
            result["error"] = self.error
        return result


@dataclass
class PaymentInfo:
    payment_id: str
    creation_date: str
    payment_date: str
    amount: str
    payment_type: str
    status: str = "unknown"

    @property
    def is_paid(self) -> bool:
        """Проверяет, оплачен ли платеж"""
        return bool(self.payment_date) and self.payment_date != "Не оплачен"
