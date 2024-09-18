# views.py (in your Django app)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from .tasks import process_csv

class FileUploadView(APIView):
    authentication_classes=[]
    permission_classes=[]
    def post(self, request, *args, **kwargs):
        file = request.FILES['file']
        file_path = default_storage.save(f'uploads/{file.name}', file)
        process_csv.delay(file_path)  
        return Response({"message": "File uploaded successfully, processing started."}, status=status.HTTP_201_CREATED)
