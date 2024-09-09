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
    columns = ['id', '2', '3', '4', '5', '6', '7', '8', '9', '0']

    if table:
        print("Has table")
        # header_row = table.find('thead') or table.find('tr')
        # if header_row:
        #     headers = header_row.find_all('th') or header_row.find_all('td')
        #     columns = [header.get_text(strip=True) for header in headers]

        rows = table.find_all('tr')
        for row in rows[6:]:
            cells = row.find_all('td')
            # if len(cells) == len(columns):
            cell_data = [cell.get_text(strip=True) for cell in cells]
            # print(cell_data)
            formatted_data = []
            for value in cell_data:
                # print(value)
                try:
                    x = value.replace('\xa0', '')
                    try:
                        formatted_value = int(x)
                    except:
                        formatted_value = float(x.replace(',', '.'))
                except:
                    formatted_value = value
                # print(formatted_value)
                formatted_data.append(formatted_value)
            data.append(formatted_data)
    else:
        print("No table")

    df = pd.DataFrame(data, columns=columns)
    print('OK: 61')
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
            # print(response.text)
            response.raise_for_status()
            if f"/uz/statistics/bankstats/{doc_id}/" in response.text:
                target_url = f"https://cbu.uz/uz/statistics/bankstats/{doc_id}/"
                links.append(target_url)
                print(target_url)
        except requests.RequestException as e:
            print(f"Error occurred: {e}")
            return HttpResponse(f"Error occurred: {e}")

    for url in links:
        print(f"URL: {url}")
        try:
            df = fetch_data_from_url(url)
            if not df.empty:
                print('119')
                for _, row in df.iterrows():
                    # print(row.get('2', 0))
                    try:
                        BankReportModel.objects.update_or_create(
                            bank_name=row.get('2', 0),
                            defaults={
                                'credits': row.get('3', 0),
                                'cred_natural_persons': row.get('4', 0),
                                'cred_legal_entities': row.get('5', 0),
                                'deposits': row.get('6', 0),
                                'dep_natural_persons': row.get('7', 0),
                                'dep_legal_entities': row.get('8', 0),
                            }
                        )
                        # BankReportModel.save()
                    except:
                        print(f"Error occurred: {row.get('2')}")
            else:
                print(f"137: {df}")
        except Exception as e:
            return HttpResponse(f"Error occurred: {e}")

    return redirect('stats')


def stats_view(request):
    bank_report = BankReportModel.objects.all()
    return render(request, 'stats.html', {'bank_credits': bank_report})


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

    return HttpResponse("Fayl all_data.xlsx nomli faylga saqlandi")
