# CMMI Project

This project is a web-based application designed to handle large data uploads, user management, and data queries efficiently. Below are key details regarding the implementation and features of the project.

## Features

- **Live Server**
    The project is deployed on a live server; however, due to server capacity limitations, large files are not supported. For large-scale deployments, upgrading the server resources is recommended.The Celery worker is configured to start automatically via the system's service management. This means you don't need to manually start or trigger the Celery worker after deployment, adding to the application's ease of maintenance.

- **File Upload with Celery**:  
  The application handles large file uploads (CSV/XLSX up to 1GB) by processing them in chunks using **Celery**. This prevents the server from being overwhelmed by large files and ensures the application remains responsive. The background task processes the uploaded file asynchronously, making use of task queues for long-running operations without blocking the main server. 
    - Celery breaks down the file into manageable chunks, updating the progress as the data is processed.
    - This approach allows the application to scale easily, handling multiple file uploads simultaneously without causing server timeouts or crashes.

- **User Management**:
    - **Registration**: New users can be registered via the Django Admin panel.
    - **Authentication**: Only logged-in users can access the **Dashboard** and other restricted pages. User authentication is handled using **Django Allauth** to provide secure login/logout functionalities.
  
- **Query Builder**:  
  Users can filter the uploaded data via the query builder interface. The filtering criteria include keywords, industry, city, state, country, year founded, and employee range.

- **Dashboard Access**:  
  Only authenticated users have access to the dashboard and file upload functionality. This ensures the system is secure, restricting access to authorized users only.

- **Background Task Handling**:  
  Celery manages background tasks for heavy operations such as file processing, ensuring that the application remains responsive. These tasks include:
    - **File upload**: Handling CSV/XLSX file uploads by processing them in chunks.
    - **Data processing**: Parsing and storing data into the database without blocking the main application.

## Technology Stack

- **Framework**: Django
- **Frontend**: Bootstrap 4 (for responsive and user-friendly design)
- **Backend**: Django REST Framework (for API handling)
- **Database**: PostgreSQL
- **Task Queue**: Celery with Redis as the broker
- **Containerization**: Docker (optional setup for deploying the application in containers)

## Getting Started

1. **Clone the repository**:  
   ```bash
   git clone <repository-url>
   cd cmmi-project
   ```

2. **Set up the virtual environment**:  
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:  
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the database**:  
   - Configure PostgreSQL in your environment settings.
   - Run migrations:
     ```bash
     python manage.py migrate
     ```

5. **Run the server**:  
   ```bash
   python manage.py runserver
   ```

6. **Start Celery**:  
   ```bash
   celery -A cmmi_project worker --loglevel=info
   ```


## File Upload with Progress Tracking

The file upload feature in this application is designed to handle large files efficiently. The upload is performed in chunks to prevent overwhelming the server. Once a file is uploaded, it is processed in the background using Celery, allowing users to continue using the system without waiting for the upload to complete.

Progress tracking is implemented, allowing users to see the status of the file processing in real-time.

## Celery Setup for Background Tasks

Celery is used to manage long-running tasks like file uploads and data processing. To run Celery, make sure Redis is running as the message broker, then start the Celery worker as shown above.

## Accessing the Admin Panel

The admin panel can be accessed at `/admin`. Use the following credentials to log in:

- Username: `admin`
- Password: `admin`

You can register new users or manage existing users through the admin interface.

## Security

- **Authentication**: Only logged-in users have access to sensitive features such as file upload and data querying.
- **CSRF Protection**: Django's built-in CSRF protection is enabled for all forms and requests.

## Additional Notes

- For any data queries or filtering, ensure that you have uploaded a valid CSV/XLSX file beforehand.
- The application is configured to work efficiently with large datasets, providing real-time feedback on query results.

## Docker

- Docker files are also included