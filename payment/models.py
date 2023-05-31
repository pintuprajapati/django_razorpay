from django.db import models
from django.utils.translation import gettext_lazy as _
from enum import Enum

class PaymentStatus(Enum):
    PENDING = "Pending"
    SUCCESS = "Success"
    FAILURE = "Failure"
    
    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

# Payment model
class Payment(models.Model):
    name = models.CharField(_("Customer Name"), max_length=254, blank=False, null=False)
    amount = models.FloatField(_("Amount"), null=False, blank=False)

    # razorpay ids
    razor_pay_order_id = models.CharField(_("Order ID"), max_length=40, null=False, blank=False)
    razor_pay_payment_id = models.CharField(_("Payment ID"), max_length=36, null=False, blank=False)
    razor_pay_payment_signature = models.CharField(_("Signature ID"), max_length=128, null=False, blank=False)
    
    # payment status
    status = models.CharField(
        _("Payment Status"),
        choices=PaymentStatus.choices(),
        default=PaymentStatus.PENDING,
        max_length=254,
        blank=False,
        null=False,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id}-{self.name}-{self.status}"
        