from django.contrib import admin
from .models import BankReportModel


class BankAdmin(admin.ModelAdmin):
    list_display = ('id', 'bank_name', 'credits', 'deposits')
    search_fields = ('bank_name',)
    ordering = ['credits', 'deposits']


admin.site.register(BankReportModel, BankAdmin)