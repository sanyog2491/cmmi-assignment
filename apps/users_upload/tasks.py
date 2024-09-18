# tasks.py
from venv import logger
from celery import shared_task
import pandas as pd
from .models import Companies

from celery import shared_task
from django.core.cache import cache
from apps.users_upload.models import Companies
import pandas as pd
import os

@shared_task(bind=True)
def process_file(self, file_path):
    try:
        # Initialize progress
        total_rows = sum(1 for row in open(file_path))  # Total number of rows in the file
        processed_rows = 0
        cache.set(f'file_progress_{file_path}', 0)
        
        file_extension = file_path.split('.')[-1].lower()
        if file_extension == 'csv':
            df = pd.read_csv(file_path)
        elif file_extension in ['xls', 'xlsx']:
            df = pd.read_excel(file_path)
        else:
            raise ValueError("Unsupported file format")

        for _, row in df.iterrows():
            Companies.objects.create(
                code=row['code'],
                name=row['name'],
                domain=row['domain'],
                year_founded=row['year founded'],
                industry=row['industry'],
                size_range=row['size range'],
                locality=row['locality'],
                country=row['country'],
                linkedin_url=row['linkedin url'],
                current_employee_estimate=row['current employee estimate'],
                total_employee_estimate=row['total employee estimate'],
            )
            processed_rows += 1
            progress = (processed_rows / total_rows) * 100
            cache.set(f'file_progress_{file_path}', progress)
        
        # Final update to ensure progress is 100%
        cache.set(f'file_progress_{file_path}', 100)
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error processing file: {e}")
