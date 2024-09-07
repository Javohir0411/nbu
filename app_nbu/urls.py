# from django.urls import path
# from app_nbu.views import (main_page,
#                            calculate_view,
#                            stats_page,
#                            analyze_credit_shares,
#                            analyze_credit_distribution,
#                            analyze_deposit_growth,
#                            download_excel
#                            )
#
# urlpatterns = [
#     path('', main_page, name='main'),
#     path('calculate/', calculate_view, name='calculate'),
#     path('stats/', stats_page, name='stats'),
#     path('analyze/deposit-growth/', analyze_deposit_growth, name='analyze_deposit_growth'),
#     path('analyze/credit-distribution/', analyze_credit_distribution, name='analyze_credit_distribution'),
#     path('analyze/credit-shares/', analyze_credit_shares, name='analyze_credit_shares'),
#     path('download/', download_excel, name='download_excel'),
# ]
from django.conf.urls.static import static
from django.urls import path

from app_nbu.utils import export_to_excel
from app_nbu.views import (calculate_view,
                           main,
                           stats_view,
                           analyze_deposit_growth,
                           analyze_credit_distribution,
                           analyze_credit_shares,
                           create_excel,
    # create_deposit_growth_chart
                           )

urlpatterns = [
    path('', main, name='main_page'),
    path('export_to_excel/', export_to_excel, name='export_to_excel'),
    path('calculate/', calculate_view, name='calculate'),
    path('stats/', stats_view, name='stats'),
    path('analyze-deposit-growth/', analyze_deposit_growth, name='analyze_deposit_growth'),
    path('analyze-credit-distribution/', analyze_credit_distribution, name='analyze_credit_distribution'),
    path('analyze-credit-shares/', analyze_credit_shares, name='analyze_credit_shares'),
    path('create-excel/', create_excel, name='create_excel'),
    # path('chart-data/', create_deposit_growth_chart, name='create_deposit_growth_chart'),
]
