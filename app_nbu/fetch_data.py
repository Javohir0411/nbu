from django.core.management import BaseCommand
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from io import StringIO
import pandas as pd
import requests
import calendar
import os


def handle(self, *args, **kwargs):
    base_url = 'https://cbu.uz/uz/statistics/bankstats/'
    months = ['01', '02', '03', '04', '05', '06', '07', '08']
    docs = ['1569299', '1613177', '1649287', '1674458', '1710841', '1746716', '1785819', '1844923']

    output_folder = 'data'
    os.makedirs(output_folder, exist_ok=True)

    for month, doc_id in zip(months, docs):
        # Yil va oy qiymatlarini aniqlash
        year = '2024'
        month_int = int(month)

        _, num_days = calendar.monthrange(int(year), month_int)
        end_date = f'{year}-{month}-{num_days:02d}'

        first_params = {
            'year': year,
            'month': month,
            'arFilter_DATE_ACTIVE_FROM_1': f'{year}-{month}-01',
            'arFilter_DATE_ACTIVE_FROM_2': end_date,
            'arFilter_ff[SECTION_ID]': '3504',
            'set_filter': 'Y'
        }
        first_query_string = urlencode(first_params)
        first_url = f"{base_url}?{first_query_string}"

        response = requests.get(first_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        if f"/uz/statistics/bankstats/{doc_id}/" in response.text:
            target_url = f"https://cbu.uz/uz/statistics/bankstats/{doc_id}/"
            print(f"{first_url} uchun topilgan sahifa URL manzili: {target_url}")

            response = requests.get(target_url)
            soup = BeautifulSoup(response.content, "html.parser")

            table = soup.find("table")  # Agar jadval ID yoki CLASS bilan tanish bo'lsa, shuni ishlating

            if table:
                table_html = str(table)
                df = pd.read_html(StringIO(table_html), flavor='bs4')[0]

                title = f"Tijorat banklarining kredit va depozitlar to`g`risida 2024-yil {month}-oy holatiga ma'lumot"
                df_combined = pd.concat([df], ignore_index=True)

                file_path = os.path.join(output_folder, f"jadval_{month}_{doc_id}.xlsx")
                df_combined.to_excel(file_path, index=False, header=False)
                print(f"Ma'lumotlar {file_path} ga saqlandi.")
            else:
                print(f"{target_url} da jadval topilmadi.")
        else:
            print(f"{first_url} da kerakli sahifa topilmadi.")
