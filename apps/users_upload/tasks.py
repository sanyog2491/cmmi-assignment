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


import pandas as pd
import openpyxl
from celery import shared_task
from apps.users_upload.models import Companies

@shared_task
def process_file(file_path):
    """
    Process a file and insert its data into the database.

    This function handles CSV and XLSX file formats. It reads the file in chunks 
    and processes each chunk to extract and insert data into the database.

    Parameters:
        file_path (str): The path to the file to be processed.

    Raises:
        ValueError: If the file format is unsupported or if the columns in an 
                    XLSX file do not match the expected columns.
    """
    file_extension = file_path.split('.')[-1].lower()
    
    chunk_size = 1000  

    if file_extension == 'csv':
        chunk_iter = pd.read_csv(file_path, chunksize=chunk_size)
        
        for chunk in chunk_iter:
            process_chunk(chunk)

    elif file_extension in ['xls', 'xlsx']:
        wb = openpyxl.load_workbook(file_path, read_only=True)
        sheet = wb.active
        rows = sheet.iter_rows(values_only=True)

        headers = next(rows)  
        expected_columns = [
            'code', 'name', 'domain', 'year founded', 'industry',
            'size range', 'locality', 'country', 'linkedin url',
            'current employee estimate', 'total employee estimate'
        ]

        if list(headers) != expected_columns:
            raise ValueError(f"File columns do not match expected columns. Found columns: {list(headers)}")

        chunk = []
        for row in rows:
            chunk.append(row)
            if len(chunk) >= chunk_size:
                process_chunk(chunk, headers)
                chunk = []  # Reset chunk

        if chunk:  
            process_chunk(chunk, headers)
    
    else:
        raise ValueError("Unsupported file format")


def process_chunk(chunk, headers=None):
    """
    Process and insert a chunk of data into the database.

    This function converts rows of data into `Companies` model instances and 
    performs a bulk insert into the database.

    Parameters:
        chunk (list of tuples): The chunk of data to be processed.
        headers (list of str, optional): The headers for XLSX files. Used to map 
                                         column names to data fields. Defaults to None.
    """    
    records = []
    for row in chunk:
        row_data = dict(zip(headers, row))
        records.append(
            Companies(
                code=row_data['code'],
                name=row_data['name'],
                domain=row_data['domain'],
                year_founded=row_data['year founded'],
                industry=row_data['industry'],
                size_range=row_data['size range'],
                locality=row_data['locality'],
                country=row_data['country'],
                linkedin_url=row_data['linkedin url'],
                current_employee_estimate=row_data['current employee estimate'],
                total_employee_estimate=row_data['total employee estimate']
            )
        )
    
    Companies.objects.bulk_create(records)