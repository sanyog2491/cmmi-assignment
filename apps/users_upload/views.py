# views.py (in your Django app)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from .tasks import process_file
from django.core.cache import cache

class FileUploadView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('data_file')
        if not file or not (file.name.endswith('.csv') or file.name.endswith('.xlsx')):
            return Response({"error": "Invalid file type. Please upload a CSV or XLSX file."}, status=status.HTTP_400_BAD_REQUEST)

        file_path = default_storage.save(f'uploads/{file.name}', file)
        process_file.delay(file_path)  # Pass file_path to Celery task


        return Response({"message": "File uploaded successfully, processing started."}, status=status.HTTP_201_CREATED)



