# from app_nbu.models import BankReportModel
# from django.http import HttpResponse
# from urllib.parse import urlencode
# from asyncio.log import logger
# from bs4 import BeautifulSoup
# from io import StringIO
# import pandas as pd
# import requests
# import io
#
#
# def save_to_database(df):
#     for _, row in df.iterrows():
#         BankReportModel.objects.create(
#             bank_name=row['Bank Name'],
#             credits=row['Credits'],
#             cred_natural_persons=row['Credits Of Natural Persons'],
#             cred_legal_entities=row['Credits Of Legal Entities'],
#             deposits=row['Deposits Amount'],
#             dep_natural_persons=row['Deposits Of Natural Persons'],
#             dep_legal_entities=row['Deposits Of Legal Entities'],
#         )
#
#
# def export_to_excel(df):
#     output = io.BytesIO()  # Xotira oqimi yaratildi
#     with pd.ExcelWriter(output, engine='openpyxl') as writer:
#         df.to_excel(writer, sheet_name='Sheet1', index=False)
#     output.seek(0)
#     response = HttpResponse(output, content_type='application/vnd.ms-excel')
#     response['Content-Disposition'] = 'attachment; filename="bank_data.xlsx"'
#     return response
#
#
# def calculate_reports(df):
#     deposit_growth = df.groupby['deposit'].sum()  # Depozit o'sishini hisoblash
#
#     # Qo'shimcha hisoblashlarni amalga oshirishingiz mumkin
#     top_banks = df.groupby('bank')['credit'].sum().sort_values(ascending=False)  # Eng ko'p kredit beruvchi banklar
#     average_deposit = df['deposit'].mean()  # O'rtacha depozit miqdori
#
#     report = {
#         'deposit_growth': deposit_growth,
#         'top_banks': top_banks,
#         'average_deposit': average_deposit
#     }
#
#     return report
#
#
# def save_to_excel(df, filename):
#     df.to_excel(filename, index=False)

import pandas as pd
from app_nbu.models import BankReportModel
import matplotlib.pyplot as plt
import io
import base64
import xlsxwriter
from django.http import HttpResponse


def save_to_database(df):
    for _, row in df.iterrows():
        BankReportModel.objects.update_or_create(
            bank_name=row.get('Bank Name', 'N/A'),
            defaults={
                'credits': row.get('Credits', 'N/A'),
                'cred_natural_persons': row.get('Credits Of Natural Persons', 'N/A'),
                'cred_legal_entities': row.get('Credits Of Legal Entities', 'N/A'),
                'deposits': row.get('Deposits Amount', 'N/A'),
                'dep_natural_persons': row.get('Deposits Of Natural Persons', 'N/A'),
                'dep_legal_entities': row.get('Deposits Of Legal Entities', 'N/A'),
            }
        )


def save_to_excel(df, filename):
    with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=False)
        workbook = writer.book
        worksheet = writer.sheets['Sheet1']
        worksheet.set_column('A:Z', 20)


def export_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=False)
        writer.save()
    output.seek(0)
    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=report.xlsx'
    return response


def calculate_reports(df):
    deposit_growth = df.groupby('bank_name')['deposits'].sum()

    top_banks = df.groupby('bank_name')['credits'].sum().sort_values(ascending=False)
    average_deposit = df['deposits'].mean()

    report = {
        'deposit_growth': deposit_growth,
        'top_banks': top_banks,
        'average_deposit': average_deposit
    }

    return report
