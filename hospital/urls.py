from django.urls import path
from hospital import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('patient/', views.patient_home, name='patient_home'),
    path('doctor/', views.doctor_home, name='doctor_home'),
    path('reception/', views.reception_home, name='reception_home'),
    path('tester/', views.tester_home, name='tester_home'),
    path('logout/', views.logout_view, name='logout'),
    
    path('patient/signup/', views.patient_signup, name='patient_signup'),
    path('patient/login/', views.patient_login, name='patient_login'),
    path('patient/dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('patient/appointments/', views.patient_appointments, name='patient_appointments'),
    path('patient/appointment/new/', views.new_appointment, name='new_appointment'),
    path('patient/history/', views.patient_history, name='patient_history'),
    
    path('doctor/signup/', views.doctor_signup, name='doctor_signup'),
    path('doctor/login/', views.doctor_login, name='doctor_login'),
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctor/appointments/', views.doctor_appointments, name='doctor_appointments'),
    path('doctor/patient/<int:patient_id>/', views.doctor_patient_detail, name='doctor_patient_detail'),
    path('doctor/appointment/<int:appointment_id>/test/', views.request_test, name='request_test'),
    path('doctor/appointment/<int:appointment_id>/prescription/', views.create_prescription, name='create_prescription'),
    path('doctor/appointment/<int:appointment_id>/analyze/', views.analyze_test_results, name='analyze_test_results'),
    
    path('reception/login/', views.receptionist_login, name='receptionist_login'),
    path('reception/dashboard/', views.receptionist_dashboard, name='receptionist_dashboard'),
    path('reception/test/<int:test_id>/manage/', views.manage_test_request, name='manage_test_request'),
    path('reception/appointment/<int:appointment_id>/assign/', views.assign_doctor, name='assign_doctor'),
    
    path('tester/login/', views.tester_login, name='tester_login'),
    path('tester/dashboard/', views.tester_dashboard, name='tester_dashboard'),
    path('tester/test/<int:test_id>/upload/', views.upload_test_result, name='upload_test_result'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)