# # tasks.py
# from celery import shared_task
# import pandas as pd
# from .models import Companies

# @shared_task
# def process_csv(file_path):
#     df = pd.read_csv(file_path)
#     for _, row in df.iterrows():
#         Companies.objects.create(
#             code=row['code'],
#             name=row['name'],
#             domain=row['domain'],
#             year_founded=row['year founded'],
#             industry=row['industry'],
#             size_range=row['size range'],
#             locality=row['locality'],
#             country=row['country'],
#             linkedin_url=row['linkedin url'],
#             current_employee_estimate=row['current employee estimate'],
#             total_employee_estimate=row['total employee estimate'],
#         )
