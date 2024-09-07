from django.db import models


class AbstractBaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        db_table = "abstract_model"


class BankReportModel(AbstractBaseModel):
    bank_name = models.CharField(max_length=255)
    credits = models.DecimalField(max_digits=12, decimal_places=2)  # max_digits qo'shildi
    cred_natural_persons = models.DecimalField(max_digits=12, decimal_places=2)  # max_digits qo'shildi
    cred_legal_entities = models.DecimalField(max_digits=12, decimal_places=2)  # max_digits qo'shildi
    deposits = models.DecimalField(max_digits=12, decimal_places=2)  # max_digits qo'shildi
    dep_natural_persons = models.DecimalField(max_digits=12, decimal_places=2)  # max_digits qo'shildi
    dep_legal_entities = models.DecimalField(max_digits=12, decimal_places=2)
    # month = models.IntegerField()

    class Meta:
        verbose_name = "Bank_report_model"
        verbose_name_plural = "Bank_report_models"
        db_table = 'bank_report_model'

    def __str__(self):
        return f"{self.bank_name}-{self.credits}: {self.deposits}"
