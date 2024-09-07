# from app_nbu.utils import (calculate_reports,
#                            save_to_excel,
#                            save_to_database,
#                            export_to_excel, )
# from django.shortcuts import render, redirect
# from app_nbu.models import BankReportModel
# from django.http import HttpResponse, JsonResponse
# from matplotlib import pyplot as plt
# from urllib.parse import urlencode
# from bs4 import BeautifulSoup
# from io import StringIO
# from config import settings
# import pandas as pd
# import requests
# import base64
# import io
# import json
# import os
#
#
# def main(request):
#     return render(request, 'main.html')
#
#
# base_url = 'https://cbu.uz/uz/statistics/bankstats/'
# months = ['01', '02', '03', '04', '05', '06', '07', '08']
# docs = ['1569299', '1613177', '1649287', '1674457', '1710841', '1746716', '1785819', '1844923']
# links = []
#
#
# def fetch_data_from_url(url):
#     response = requests.get(url)
#     soup = BeautifulSoup(response.text, 'html.parser')
#     table = soup.find('table')
#
#     data = []
#     columns = []
#
#     if table:
#         header_row = table.find('thead')  # Agar ustun nomlari <thead> ichida bo'lsa
#         if not header_row:
#             header_row = table.find('tr')  # Agar ustun nomlari <tr> ichida bolsa (jadvalni birinchi satri)
#
#         if header_row:
#             headers = header_row.find_all('th')
#             if not headers:
#                 headers = header_row.find_all('td')
#             columns = [header.get_text(strip=True) for header in headers]
#
#         rows = table.find_all('tr')
#         for row in rows[1:]:  # Birinchi satrni ochirib tashlash (ustunlar satri)
#             cells = row.find_all('td')
#             if len(cells) == len(columns):
#                 cell_data = [cell.get_text(strip=True) for cell in cells]
#
#                 # Sonli ma'lumotlarni decimal formatga o'tkazish
#                 formatted_data = []
#                 for value in cell_data:
#                     try:
#                         # Sonlarni decimal formatga o'tkazish
#                         formatted_value = float(value.replace(',', '.'))
#                     except ValueError:
#                         formatted_value = value
#                     formatted_data.append(formatted_value)
#
#                 data.append(formatted_data)
#
#     df = pd.DataFrame(data, columns=columns)
#     return df
#
#
# # Asosiy funksiya va ma'lumotlarni yig'ish
# def process_data(request):
#     data = []
#     for month, doc_id in zip(months, docs):
#         first_parameters = {
#             'year': '2024',
#             'month': month,
#             'arFilter_DATE_ACTIVE_FROM_1': f'2024-{month}-01',
#             'arFilter_DATE_ACTIVE_FROM_2': f'2024-{month}-28',
#             'arFilter_ff[SECTION_ID]': '3504',
#             'set_filter': 'Y'
#         }
#
#         first_query_string = urlencode(first_parameters)
#         first_url = f"{base_url}?{first_query_string}"
#
#         headers = {
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
#         }
#
#         cookies = {'cookie_name': 'cookie_value'}
#         response = requests.get(first_url, headers=headers, cookies=cookies)
#
#         if response.status_code != 200:
#             print(f"Response status code: {response.status_code} for URL: {first_url}")
#             continue
#
#         print(f"Response status code: {response.status_code} for URL: {first_url}")
#         if f"/uz/statistics/bankstats/{doc_id}/" in response.text:
#             target_url = f"https://cbu.uz/uz/statistics/bankstats/{doc_id}/"
#             try:
#                 df = fetch_data_from_url(target_url)  # Yangi funksiya orqali jadval ma'lumotlarini olish
#                 if not df.empty:
#                     data.append(df)
#             except Exception as e:
#                 print(f"Xato yuz berdi: {e}")
#
#     if request.method == 'POST':
#         # Ma'lumotlarni keyingi funksiyalarda ishlating
#         save_to_database(data)
#         export_to_excel(data)
#         report = calculate_reports(data)
#         save_to_excel(data, 'report.xlsx')
#         return render(request, 'list.html', {'report': report})
#
#     return redirect('main')
#
#
# def calculate_view(request):
#     links = []  # Linklani saqlash uchun bo'sh ro'yxat
#     for month, doc_id in zip(months, docs):
#         first_parameters = {
#             'year': '2024',
#             'month': month,
#             'arFilter_DATE_ACTIVE_FROM_1': f'2024-{month}-01',
#             'arFilter_DATE_ACTIVE_FROM_2': f'2024-{month}-28',
#             'arFilter_ff[SECTION_ID]': '3504',
#             'set_filter': 'Y'
#         }
#
#         first_query_string = urlencode(first_parameters)
#         first_url = f"{base_url}?{first_query_string}"
#
#         headers = {
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
#         }
#
#         cookies = {'cookie_name': 'cookie_value'}
#         try:
#             response = requests.get(first_url, headers=headers, cookies=cookies)
#             response.raise_for_status()  # Xatoni avtomatik chiqarish
#
#             print(f"Response status code: {response.status_code} for URL: {first_url}")
#             soup = BeautifulSoup(response.text, 'html.parser')
#
#             if f"/uz/statistics/bankstats/{doc_id}/" in response.text:
#                 target_url = f"https://cbu.uz/uz/statistics/bankstats/{doc_id}/"
#                 links.append(target_url)
#
#         except requests.RequestException as e:
#             return HttpResponse(f"Xato yuz berdi: {e}")
#
#     for url in links:
#         try:
#             df = fetch_data_from_url(url)  # fetch_data_from_url() funksiyasini chaqirish
#             if not df.empty:
#                 print("DataFrame ustun nomlari:", df.columns)  # Ustun nomlarini tekshirish
#                 for index, row in df.iterrows():
#                     # Ustun nomlarini tekshirish va moslashtirish
#                     BankReportModel.objects.create(
#                         bank_name=row.get('bank_name', 'N/A'),
#                         deposits=row.get('deposits', 'N/A'),
#                         credits=row.get('credits', 'N/A')
#                     )
#         except Exception as e:
#             return HttpResponse(f"Xato yuz berdi: {e}")
#
#     return redirect('stats')
#
#
# def stats_view(request):
#     bank_report = BankReportModel.objects.all()
#     return render(request, 'stats.html', {'bank_report_model': bank_report})
#
#
# def create_deposit_growth_chart(data):
#     data = list(
#         BankReportModel.objects.values('bank_name',
#                                        'credits',
#                                        'deposits'))
#
#     return JsonResponse(data, safe=False)
#
#
# def analyze_deposit_growth(request):
#     data = BankReportModel.objects.all()
#
#     df = pd.DataFrame(list(data.values()))
#
#     total_deposits = df.groupby('bank_name')['deposits'].sum()
#     highest_deposit_bank = total_deposits.idxmax()
#     highest_deposit_amount = total_deposits.max()
#
#     deposit_share = (total_deposits / total_deposits.sum()) * 100
#
#     plt.figure(figsize=(8, 6))
#     plt.pie(deposit_share, labels=deposit_share.index, autopct='%1.1f%%')
#     plt.title('Deposit Share by Bank')
#
#     pie_chart = io.BytesIO()
#     plt.savefig(pie_chart, format='png')
#     pie_chart.seek(0)
#     pie_chart_url = base64.b64encode(pie_chart.getvalue()).decode('utf-8')
#
#     context = {
#         'bank_report': data,
#         'total_deposits': total_deposits,
#         'highest_deposit_bank': highest_deposit_bank,
#         'highest_deposit_amount': highest_deposit_amount,
#         'pie_chart_url': pie_chart_url,
#     }
#
#     return render(request, 'analyze_deposit_growth.html', context)
#
#
# def analyze_credit_distribution(request):
#     data = BankReportModel.objects.all()
#     df = pd.DataFrame(list(data.values()))
#
#     if df.empty:
#         return HttpResponse("analyze_credit_distribution Hech qanday ma'lumot topilmadi.")
#
#     df_grouped = df.groupby('bank_name').agg({
#         'credits': 'sum'
#     }).reset_index()
#
#     total_credits = df_grouped['credits'].sum()
#
#     # Hisoblangan miqdorlar bilan DataFrame'ga 'percentage' ustunini qo'shish
#     df_grouped['percentage'] = (df_grouped['credits'] / total_credits) * 100
#
#     top_banks = df_grouped.sort_values(by='credits', ascending=False)
#
#     result = "Eng katta miqdordagi kreditlarga ega banklar va ulushlari:\n\n"
#     for _, row in top_banks.iterrows():
#         result += f"Bank: {row['bank_name']}, Kreditlar: {row['credits']}, Ulush: {row['percentage']:.2f}%<br>"
#
#     return HttpResponse(result)
#
#
# def analyze_credit_shares(request):
#     # Ma'lumotlarni olish
#     data = BankReportModel.objects.all()
#     df = pd.DataFrame(list(data.values()))
#
#     # Agar DataFrame bo'sh bo'lsa
#     if df.empty:
#         return HttpResponse("analyze_credit_shares Hech qanday ma'lumot topilmadi.")
#
#     # Kreditlarni banklar bo'yicha guruhlash
#     bank_credits = df.groupby('bank_name')['credits'].sum().reset_index()
#
#     # Jami kreditlar hisoblash
#     total_credits = bank_credits['credits'].sum()
#
#     # Kredit ulushlarini hisoblash
#     bank_credits['share'] = (bank_credits['credits'] / total_credits) * 100
#
#     # Chart uchun ma'lumotlar
#     chart_data = bank_credits[['bank_name', 'share']].to_dict(orient='records')
#
#     # Kontekstni tayyorlash
#     context = {
#         'bank_credits': bank_credits.to_dict(orient='records'),
#         'total_credits': total_credits,
#         'chart_data': chart_data,
#     }
#
#     # Shablonni render qilish
#     return render(request, 'stats.html', context)
#
#
# def create_excel(request):
#     com_url = 'https://cbu.uz/uz/statistics/bankstats/'
#     doc_months = ['01', '02', '03', '04', '05', '06', '07', '08']
#     docums_id = ['1569299', '1613177', '1649287', '1674457', '1710841', '1746716', '1785819', '1844923']
#     links = []
#     all_data = []
#
#     for month, doc_id in zip(doc_months, docums_id):
#         first_param = {
#             'year': '2024',
#             'month': month,
#             'arFilter_DATE_ACTIVE_FROM_1': f'2024-{month}-01',
#             'arFilter_DATE_ACTIVE_FROM_2': f'2024-{month}-28',
#             'arFilter_ff[SECTION_ID]': '3504',
#             'set_filter': 'Y'
#         }
#         first_query_string = urlencode(first_param)
#         first_url = f"{com_url}?{first_query_string}"
#
#         response = requests.get(first_url)
#
#         if f"/uz/statistics/bankstats/{doc_id}/" in response.text:
#             target_url = f"https://cbu.uz/uz/statistics/bankstats/{doc_id}/"
#             links.append(target_url)
#
#     for link in links:
#         response = requests.get(link)
#         soup = BeautifulSoup(response.content, 'html.parser')
#         table = soup.find('table')
#         if table:
#             table_html = str(table)
#             df = pd.read_html(StringIO(table_html))[0]
#             all_data.append(df)
#
#     # Ma'lumotlarni bitta DataFrame ga birlashtiring
#     if all_data:
#         combined_df = pd.concat(all_data, ignore_index=True)
#     else:
#         combined_df = pd.DataFrame()
#
#     response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
#     response['Content-Disposition'] = 'attachment; filename="report.xlsx"'
#
#     with pd.ExcelWriter(response, engine='openpyxl') as writer:
#         combined_df.to_excel(writer, index=False, sheet_name='Sheet1')
#
#     return response

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from app_nbu.models import BankReportModel
from app_nbu.utils import (save_to_excel, save_to_database, export_to_excel, calculate_reports)
from urllib.parse import urlencode
from bs4 import BeautifulSoup
import pandas as pd
import requests
import io
import base64
import matplotlib.pyplot as plt

base_url = 'https://cbu.uz/uz/statistics/bankstats/'
months = ['01', '02', '03', '04', '05', '06', '07', '08']
docs = ['1569299', '1613177', '1649287', '1674457', '1710841', '1746716', '1785819', '1844923']


def main(request):
    return render(request, 'main.html')


def fetch_data_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table')

    data = []
    columns = []

    if table:
        header_row = table.find('thead') or table.find('tr')
        if header_row:
            headers = header_row.find_all('th') or header_row.find_all('td')
            columns = [header.get_text(strip=True) for header in headers]

        rows = table.find_all('tr')
        for row in rows[1:]:
            cells = row.find_all('td')
            if len(cells) == len(columns):
                cell_data = [cell.get_text(strip=True) for cell in cells]
                formatted_data = []
                for value in cell_data:
                    try:
                        formatted_value = float(value.replace(',', '.'))
                    except ValueError:
                        formatted_value = value
                    formatted_data.append(formatted_value)
                data.append(formatted_data)

    df = pd.DataFrame(data, columns=columns)
    return df


def process_data(request):
    data = []
    for month, doc_id in zip(months, docs):
        first_parameters = {
            'year': '2024',
            'month': month,
            'arFilter_DATE_ACTIVE_FROM_1': f'2024-{month}-01',
            'arFilter_DATE_ACTIVE_FROM_2': f'2024-{month}-31',
            'arFilter_ff[SECTION_ID]': '3504',
            'set_filter': 'Y'
        }
        first_query_string = urlencode(first_parameters)
        first_url = f"{base_url}?{first_query_string}"

        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(first_url, headers=headers)

        if response.status_code == 200 and f"/uz/statistics/bankstats/{doc_id}/" in response.text:
            target_url = f"https://cbu.uz/uz/statistics/bankstats/{doc_id}/"
            try:
                df = fetch_data_from_url(target_url)
                if not df.empty:
                    data.append(df)
            except Exception as e:
                print(f"Error occurred: {e}")

    if request.method == 'POST':
        combined_df = pd.concat(data, ignore_index=True) if data else pd.DataFrame()
        save_to_database(combined_df)
        export_to_excel(combined_df)
        report = calculate_reports(combined_df)
        save_to_excel(combined_df, 'report.xlsx')
        return render(request, 'list.html', {'report': report})

    return redirect('main')


def calculate_view(request):
    links = []
    for month, doc_id in zip(months, docs):
        first_parameters = {
            'year': '2024',
            'month': month,
            'arFilter_DATE_ACTIVE_FROM_1': f'2024-{month}-01',
            'arFilter_DATE_ACTIVE_FROM_2': f'2024-{month}-31',
            'arFilter_ff[SECTION_ID]': '3504',
            'set_filter': 'Y'
        }
        first_query_string = urlencode(first_parameters)
        first_url = f"{base_url}?{first_query_string}"

        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            response = requests.get(first_url, headers=headers)
            response.raise_for_status()
            if f"/uz/statistics/bankstats/{doc_id}/" in response.text:
                target_url = f"https://cbu.uz/uz/statistics/bankstats/{doc_id}/"
                links.append(target_url)
        except requests.RequestException as e:
            return HttpResponse(f"Error occurred: {e}")

    for url in links:
        try:
            df = fetch_data_from_url(url)
            if not df.empty:
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
        except Exception as e:
            return HttpResponse(f"Error occurred: {e}")

    return redirect('stats')


def stats_view(request):
    bank_report = BankReportModel.objects.all()
    return render(request, 'stats.html', {'bank_report_model': bank_report})


def analyze_deposit_growth(request):
    data = BankReportModel.objects.all()
    df = pd.DataFrame(list(data.values()))

    total_deposits = df.groupby('bank_name')['deposits'].sum()
    highest_deposit_bank = total_deposits.idxmax()
    highest_deposit_amount = total_deposits.max()

    deposit_share = (total_deposits / total_deposits.sum()) * 100

    plt.figure(figsize=(8, 6))
    plt.pie(deposit_share, labels=deposit_share.index, autopct='%1.1f%%')
    plt.title('Deposit Share by Bank')

    pie_chart = io.BytesIO()
    plt.savefig(pie_chart, format='png')
    pie_chart.seek(0)
    pie_chart_url = base64.b64encode(pie_chart.getvalue()).decode('utf-8')

    context = {
        'bank_report': data,
        'total_deposits': total_deposits,
        'highest_deposit_bank': highest_deposit_bank,
        'highest_deposit_amount': highest_deposit_amount,
        'pie_chart_url': pie_chart_url,
    }

    return render(request, 'analyze_deposit_growth.html', context)


def analyze_credit_distribution(request):
    data = BankReportModel.objects.all()
    df = pd.DataFrame(list(data.values()))

    if df.empty:
        return HttpResponse("No data found for credit distribution.")

    df_grouped = df.groupby('bank_name').agg({'credits': 'sum'}).reset_index()
    total_credits = df_grouped['credits'].sum()
    df_grouped['percentage'] = (df_grouped['credits'] / total_credits) * 100

    top_banks = df_grouped.sort_values(by='credits', ascending=False)
    result = "Banks with the highest credit amounts and their shares:<br><br>"
    for _, row in top_banks.iterrows():
        result += f"Bank: {row['bank_name']}, Credits: {row['credits']}, Share: {row['percentage']:.2f}%<br>"

    return HttpResponse(result)


def analyze_credit_shares(request):
    data = BankReportModel.objects.all()
    df = pd.DataFrame(list(data.values()))

    if df.empty:
        return HttpResponse("No data found for credit shares.")

    bank_credits = df.groupby('bank_name')['credits'].sum().reset_index()
    total_credits = bank_credits['credits'].sum()
    bank_credits['share'] = (bank_credits['credits'] / total_credits) * 100

    context = {
        'bank_credits': bank_credits.to_dict(orient='records'),
        'total_credits': total_credits,
    }

    return render(request, 'stats.html', context)


def create_excel(request):
    com_url = 'https://cbu.uz/uz/statistics/bankstats/'
    doc_months = ['01', '02', '03', '04', '05', '06', '07', '08']
    docums_id = ['1569299', '1613177', '1649287', '1674457', '1710841', '1746716', '1785819', '1844923']
    links = []
    all_data = []

    for month, doc_id in zip(doc_months, docums_id):
        first_param = {
            'year': '2024',
            'month': month,
            'arFilter_DATE_ACTIVE_FROM_1': f'2024-{month}-01',
            'arFilter_DATE_ACTIVE_FROM_2': f'2024-{month}-31',
            'arFilter_ff[SECTION_ID]': '3504',
            'set_filter': 'Y'
        }
        first_query_string = urlencode(first_param)
        first_url = f"{com_url}?{first_query_string}"

        try:
            response = requests.get(first_url)
            if response.status_code == 200 and f"/uz/statistics/bankstats/{doc_id}/" in response.text:
                target_url = f"https://cbu.uz/uz/statistics/bankstats/{doc_id}/"
                links.append(target_url)
        except Exception as e:
            return HttpResponse(f"Error occurred: {e}")

    for link in links:
        try:
            df = fetch_data_from_url(link)
            if not df.empty:
                all_data.append(df)
        except Exception as e:
            return HttpResponse(f"Error occurred: {e}")

    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        save_to_excel(combined_df, 'all_data.xlsx')

    return redirect('stats')
