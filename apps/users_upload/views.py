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


class FileUploadView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('data_file')
        if not file or not (file.name.endswith('.csv') or file.name.endswith('.xlsx')):
            return Response({"error": "Invalid file type. Please upload a CSV or XLSX file."}, status=status.HTTP_400_BAD_REQUEST)

        file_path = default_storage.save(f'uploads/{file.name}', file)
        process_file.delay(file_path) 


        return Response({"message": "File uploaded successfully, processing started."}, status=status.HTTP_201_CREATED)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from apps.users_upload.models import Companies

class QueryBuilderView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Extract query parameters
        keyword = request.query_params.get('keyword', '')
        industry = request.query_params.get('industry', '')
        year_founded = request.query_params.get('year_founded', '')
        city = request.query_params.get('city', '')
        state = request.query_params.get('state', '')
        country = request.query_params.get('country', '')
        employees_from = request.query_params.get('employees_from', None)
        employees_to = request.query_params.get('employees_to', None)
        
        query = Companies.objects.all()
        print("keyword",keyword)
        # Filter by keyword (search across multiple columns)
        if keyword:
            query = query.filter(
                Q(code__icontains=keyword) |
                Q(name__icontains=keyword) |
                Q(domain__icontains=keyword) |
                Q(industry__icontains=keyword) |
                Q(locality__icontains=keyword)
            )
            print('query',query)

        # Filter by industry
        if industry:
            query = query.filter(name=industry)
            print('querys',query)

        # Filter by year founded
        if year_founded:
            query = query.filter(year_founded=year_founded)

        # Filter by city, state, country (locality column split by commas)
        if city or state or country:
            if city:
                query = query.filter(locality__icontains=city)
            if state:
                query = query.filter(locality__icontains=state)
            if country:
                query = query.filter(locality__icontains=country)

        # Filter by employees range
        if employees_from and employees_to:
            query = query.filter(
                Q(current_employee_estimate__gte=employees_from) &
                Q(current_employee_estimate__lte=employees_to)
            )

        # Return the count of matching records
        count = query.count()
        print('count',count)
        return Response({'count': count}, status=status.HTTP_200_OK)

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class ChunkPagination(PageNumberPagination):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    page_size = 10

class IndustryDropdownView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        paginator = ChunkPagination()
        industries = Companies.objects.values_list('name', flat=True).distinct()
        paginated_industries = paginator.paginate_queryset(industries, request)
        return paginator.get_paginated_response(paginated_industries)

class LocalityDropdownView(APIView):
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
                # If locality is None, add None to sets
                cities.add(None)
                states.add(None)
                countries.add(None)

        return paginator.get_paginated_response({
            'cities': list(cities),
            'states': list(states),
            'countries': list(countries)
        })