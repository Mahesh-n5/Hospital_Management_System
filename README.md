## Hospital Managemnet System 
The Hospital Management System (HMS) is a web-based application designed to streamline hospital operations by managing patient records, appointments, test results, and prescriptions. It features four distinct user roles—Receptionist, Patient, Doctor, and Tester—each with a dedicated interface and specific functionalities. The system is built using Django, Python, HTML, Bootstrap, and MySQL, ensuring a responsive and user-friendly experience.

User Roles and Functionalities:

Receptionist:
Register new patients, doctors, and testers.
Assign doctors to patient appointments.
View and manage appointment schedules.
Access patient details and appointment history.
Patient:
Register and log in to view their profile.
Book appointments with doctors.
View appointment history and test results.
Access patient history, including past appointments, test reports, and prescriptions.
Doctor:
View assigned appointments and patient details.
Request tests for patients, triggering an "Analyze" button in the doctor portal.
Create and manage prescriptions.
View patient history, including test reports and past prescriptions.
Tester:
Upload test reports (PDF format) after approval.
View and manage test-related data.
Ensure test reports are visible to doctors and patients.

Key Features:
Appointment Management: Patients can book appointments, and receptionists can assign doctors. The system prevents scheduling conflicts.
Test Result Management: Testers upload PDF test reports, which are processed to extract deviated values and matched with consequences from a dataset (cbc_low_high_dataset.csv).
Analyze Button: Appears in the doctor portal after a test is requested, allowing doctors to view and analyze test results.
Patient History: Displays appointments, test results, and prescriptions for patients and doctors.
Secure Authentication: Role-based access with encrypted passwords for all users.
File Storage: Uses FileSystemStorage for test report uploads.
Responsive UI: Built with Bootstrap for a consistent and mobile-friendly interface.

Requirements:
Python 3.8+
Django 3.2+
MySQL 5.7+
pdfplumber and pdfminer.six for PDF processing
fuzzywuzzy for test name matching
azure-storage-blob (optional, if using Azure storage instead of FileSystemStorage)

How to run:
1) install all dependencies:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
2) configure the database:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'hms',
        'USER': '<your-username>',
        'PASSWORD': '<your-password>',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
3) configure File storage database:
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
4) Run Migrations:
python manage.py makemigrations
python manage.py migrate
5) Start the development server:
python manage.py runserver

Access the application at http://localhost:8000.
