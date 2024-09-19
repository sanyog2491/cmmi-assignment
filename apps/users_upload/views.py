# views.py (in your Django app)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from .tasks import process_file
from django.core.cache import cache
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from django.views.decorators.csrf import csrf_exempt

from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from apps.users_upload.models import Companies


class FileUploadView(APIView):
    """
    API view for handling file uploads.

    This view allows authenticated users to upload CSV or XLSX files. 
    Upon successful upload, the file is saved to the server and a background 
    task is initiated to process the file asynchronously.

    Authentication:
        Requires session authentication and user must be authenticated.

    Methods:
        post(request, *args, **kwargs):
            Handles POST requests to upload a file. The file must be of type 
            CSV or XLSX. If the file is valid, it is saved to the server's 
            'uploads' directory and a background task is triggered to process 
            the file using Celery.

            Request Parameters:
                - data_file: The file to be uploaded. Must be a CSV or XLSX file.

            Returns:
                - JSON response indicating success or error. On success, a message 
                  is returned with status code 201 (Created). On failure due to 
                  invalid file type, an error message is returned with status code 
                  400 (Bad Request).
    """
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('data_file')
        if not file or not (file.name.endswith('.csv') or file.name.endswith('.xlsx')):
            return Response({"error": "Invalid file type. Please upload a CSV or XLSX file."}, status=status.HTTP_400_BAD_REQUEST)

        file_path = default_storage.save(f'uploads/{file.name}', file)
        process_file.delay(file_path) 


        return Response({"message": "File uploaded successfully, processing started."}, status=status.HTTP_201_CREATED)



class QueryBuilderView(APIView):
    """
    API view to perform filtered queries on company data.

    This view allows users to filter company data based on various criteria 
    including keyword, industry, year founded, city, state, country, and 
    employee range. The filtered results are used to return a count of 
    records matching the specified criteria.

    Authentication:
        Requires session authentication and user must be authenticated.

    Methods:
        get(request, *args, **kwargs):
            Handles GET requests to retrieve the count of company records 
            that match the provided filter criteria. The filters include:
            - keyword: Searches across multiple fields (code, name, domain, 
              industry, locality).
            - industry: Filters by the industry name.
            - year_founded: Filters by the year the company was founded.
            - city, state, country: Filters by locality, split into city, 
              state, and country.
            - employees_from, employees_to: Filters by the range of current 
              employee estimates.
            
            The method returns a JSON response with the count of records that 
            match the filters.
    """
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        keyword = request.query_params.get('keyword', '')
        industry = request.query_params.get('industry', '')
        year_founded = request.query_params.get('year_founded', '')
        city = request.query_params.get('city', '')
        state = request.query_params.get('state', '')
        country = request.query_params.get('country', '')
        employees_from = request.query_params.get('employees_from', None)
        employees_to = request.query_params.get('employees_to', None)
        
        query = Companies.objects.all()

        if keyword:
            query = query.filter(
                Q(code__icontains=keyword) |
                Q(name__icontains=keyword) |
                Q(domain__icontains=keyword) |
                Q(industry__icontains=keyword) |
                Q(locality__icontains=keyword)
            )


        if industry:
            
            query = query.filter(name=industry)

        if year_founded:
            query = query.filter(year_founded=year_founded)

        if city or state or country:
            if city:
                query = query.filter(locality__icontains=city)
            if state:
                query = query.filter(locality__icontains=state)
            if country:
                query = query.filter(locality__icontains=country)

        if employees_from and employees_to:
            query = query.filter(
                Q(current_employee_estimate__gte=employees_from) &
                Q(current_employee_estimate__lte=employees_to)
            )

        count = query.count()
        return Response({'count': count}, status=status.HTTP_200_OK)

class ChunkPagination(PageNumberPagination):
    """
    Custom pagination class for handling paginated responses in API views.

    This pagination class sets the page size to 10 records per page. It does not 
    handle authentication or permission, as it is intended solely for pagination.

    Attributes:
        page_size (int): Number of items per page, set to 10.
    """
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    page_size = 10

class IndustryDropdownView(APIView):
    """
    API view to retrieve paginated industry data.

    This view provides a list of unique industry names extracted from the 'name' 
    field of the Companies model. The data is paginated to manage large result 
    sets efficiently.

    Authentication:
        Requires session authentication and user must be authenticated.

    Methods:
        get(request, *args, **kwargs):
            Handles GET requests to retrieve paginated lists of industry names. 
            Each industry name is retrieved from the 'name' field of the Companies 
            model and paginated to ensure efficient data handling.
            Returns paginated data containing a list of unique industry names.
    """
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        paginator = ChunkPagination()
        industries = Companies.objects.values_list('name', flat=True).distinct()
        paginated_industries = paginator.paginate_queryset(industries, request)
        return paginator.get_paginated_response(paginated_industries)

class LocalityDropdownView(APIView):
    """
    API view to retrieve paginated locality data.

    This view provides a list of unique cities, states, and countries 
    extracted from the 'locality' field of the Companies model. The data 
    is paginated to handle large result sets efficiently.

    Authentication:
        Requires session authentication and user must be authenticated.

    Methods:
        get(request, *args, **kwargs):
            Handles GET requests to retrieve paginated lists of cities, states, 
            and countries. Each locality is split into city, state, and country 
            based on the format 'city, state, country'. 
            Returns paginated data containing lists of unique cities, states, 
            and countries.

    """
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        paginator = ChunkPagination()
        localities = Companies.objects.values_list('locality', flat=True).distinct()
        paginated_localities = paginator.paginate_queryset(localities, request)
        
        cities, states, countries = set(), set(), set()
        
        for locality in paginated_localities:
            if locality: 
                parts = locality.split(',')
                if len(parts) == 3:
                    city, state, country = parts
                    cities.add(city.strip() if city else None)
                    states.add(state.strip() if state else None)
                    countries.add(country.strip() if country else None)
                else:
                    cities.add(None)
                    states.add(None)
                    countries.add(None)
            else:
                cities.add(None)
                states.add(None)
                countries.add(None)

        return paginator.get_paginated_response({
            'cities': list(cities),
            'states': list(states),
            'countries': list(countries)
        })