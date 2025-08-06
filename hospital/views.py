from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse, HttpResponseForbidden
from django.db.models import Q
from datetime import date
from django.utils import timezone
from .models import (
    User, Patient, Appointment, TestType, 
    TestRequest, TestResult, Prescription, Medicine
)
from .forms import (
    PatientSignUpForm, DoctorSignUpForm, AppointmentForm,
    TestRequestForm, TestResultForm, PrescriptionForm, MedicineForm,
    PatientLoginForm, DoctorLoginForm, ReceptionistLoginForm, TesterLoginForm
)
import pdfplumber
import pandas as pd
import re
import os
from django.conf import settings

# Define column aliases for PDF parsing
HEADER_ALIASES = {
    "test": ["test", "investigation", "parameter", "name"],
    "value": ["value", "result", "observed", "reading"],
    "unit": ["unit", "units", "measurement", "measure"],
    "reference": ["reference", "range", "normal", "reference range"]
}

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF using pdfplumber"""
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
    return text

def match_header_line(line):
    tokens = re.split(r'\s{2,}', line.strip())
    found = {key: None for key in HEADER_ALIASES}

    for idx, token in enumerate(tokens):
        token_lower = token.lower().strip()
        for key, aliases in HEADER_ALIASES.items():
            if any(alias in token_lower for alias in aliases):
                found[key] = idx

    if all(v is not None for v in found.values()):
        return found
    return None

def parse_table_lines(lines, header_map, start_index):
    results = []
    for line in lines[start_index + 1:]:
        if re.search(r'(end of report|clinical notes|doctor|pathologist|sample collection)', line, re.IGNORECASE):
            break
        tokens = re.split(r'\s{2,}', line.strip())
        if len(tokens) < max(header_map.values()) + 1:
            continue
        try:
            test = tokens[header_map["test"]].strip()
            value_str = tokens[header_map["value"]].strip()
            ref_str = tokens[header_map["reference"]].strip()

            value_match = re.match(r"(L|H)?\s*(\d+(?:\.\d+)?)(?:\s*(L|H))?", value_str)
            if not value_match:
                continue
            flag = value_match.group(1) or value_match.group(3)
            value = float(value_match.group(2))

            ref_vals = re.findall(r"\d+(?:\.\d+)?", ref_str)
            if len(ref_vals) >= 2:
                low, high = float(ref_vals[0]), float(ref_vals[1])
            elif "<" in ref_str and len(ref_vals) == 1:
                low, high = 0, float(ref_vals[0])
            else:
                continue

            if not flag:
                if value < low:
                    flag = "Low"
                elif value > high:
                    flag = "High"
                else:
                    continue  # Skip normal values

            results.append({
                "Test": test,
                "Status": flag
            })
        except Exception:
            continue
    return results

def fallback_regex_extraction(text):
    lines = text.split("\n")
    results = []
    for line in lines:
        match = re.match(
            r'([A-Za-z ()/%-]{3,50})\s+(\d+(?:\.\d+)?)\s*(Low|High|Borderline)?\s+(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*([a-zA-Z/%]+)',
            line, re.IGNORECASE
        )
        if match:
            test = match.group(1).strip()
            value = float(match.group(2))
            flag = match.group(3)
            low = float(match.group(4))
            high = float(match.group(5))

            if not flag:
                if value < low:
                    flag = "Low"
                elif value > high:
                    flag = "High"
                else:
                    continue

            results.append({
                "Test": test,
                "Status": flag
            })
    return results

def extract_abnormal_results(text):
    lines = text.split("\n")
    all_results = []

    for idx, line in enumerate(lines):
        header_map = match_header_line(line)
        if header_map:
            results = parse_table_lines(lines, header_map, idx)
            all_results.extend(results)

    if not all_results:
        all_results = fallback_regex_extraction(text)

    return all_results

# Utility functions
def is_patient(user):
    return user.is_authenticated and user.is_patient

def is_doctor(user):
    return user.is_authenticated and user.is_doctor

def is_receptionist(user):
    return user.is_authenticated and user.is_receptionist

def is_tester(user):
    return user.is_authenticated and user.is_tester

# Home and Authentication Views
def home(request):
    return render(request, 'hospital/home.html')

def patient_home(request):
    return render(request, 'hospital/patient_home.html')

def doctor_home(request):
    return render(request, 'hospital/doctor_home.html')

def reception_home(request):
    return render(request, 'hospital/reception_home.html')

def tester_home(request):
    return render(request, 'hospital/tester_home.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

# Patient Views
def patient_signup(request):
    if request.method == 'POST':
        form = PatientSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('patient_home')
    else:
        form = PatientSignUpForm()
    return render(request, 'hospital/patient_signup.html', {'form': form})

def patient_login(request):
    if request.user.is_authenticated and is_patient(request.user):
        return redirect('patient_dashboard')
        
    if request.method == 'POST':
        form = PatientLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None and is_patient(user):
                login(request, user)
                messages.success(request, f'Welcome back, {user.get_full_name()}!')
                return redirect('patient_dashboard')
            else:
                messages.error(request, 'Invalid credentials or not a patient account.')
        else:
            messages.error(request, 'Invalid form data. Please try again.')
    else:
        form = PatientLoginForm()
    return render(request, 'hospital/patient_login.html', {'form': form})

@login_required
@user_passes_test(is_patient)
def patient_dashboard(request):
    patient = request.user.patient
    today = date.today()
    appointments = Appointment.objects.filter(
        patient=patient,
        date__gte=today
    ).order_by('date', 'time_slot')[:5]
    test_results = TestResult.objects.filter(
        test_request__appointment__patient=patient,
        test_request__status='COM'
    ).order_by('-completed_at')[:5]
    
    context = {
        'patient': patient,
        'appointments': appointments,
        'test_results': test_results,
    }
    return render(request, 'hospital/patient_dashboard.html', context)

@login_required
@user_passes_test(is_patient)
def patient_appointments(request):
    patient = request.user.patient
    appointments = Appointment.objects.filter(patient=patient).order_by('-date', '-time_slot')
    
    context = {
        'patient': patient,
        'appointments': appointments,
    }
    return render(request, 'hospital/patient_appointments.html', context)

@login_required
@user_passes_test(is_patient)
def new_appointment(request):
    patient = request.user.patient
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = patient
            appointment.status = 'PEN'
            appointment.save()
            messages.success(request, 'Appointment requested! Reception will assign a doctor soon.')
            return redirect('patient_dashboard')
    else:
        form = AppointmentForm()
    
    context = {
        'patient': patient,
        'form': form,
    }
    return render(request, 'hospital/new_appointment.html', context)

@login_required
@user_passes_test(is_patient)
def patient_history(request):
    patient = request.user.patient
    appointments = Appointment.objects.filter(patient=patient, status='COM')
    
    appointment_data = []
    for appointment in appointments:
        test_results = TestResult.objects.filter(
            test_request__appointment=appointment
        )
        prescriptions = Prescription.objects.filter(
            appointment=appointment
        )
        appointment_data.append({
            'appointment': appointment,
            'test_results': test_results,
            'prescriptions': prescriptions,
        })
    
    context = {
        'patient': patient,
        'appointment_data': appointment_data,
    }
    return render(request, 'hospital/patient_history.html', context)

# Doctor Views
def doctor_signup(request):
    if request.method == 'POST':
        form = DoctorSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('doctor_dashboard')
    else:
        form = DoctorSignUpForm()
    return render(request, 'hospital/doctor_signup.html', {'form': form})

def doctor_login(request):
    if request.method == 'POST':
        form = DoctorLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, Dr. {user.get_full_name()}!')
                return redirect('doctor_dashboard')
    else:
        form = DoctorLoginForm()
    return render(request, 'hospital/doctor_login.html', {'form': form})

@login_required
@user_passes_test(is_doctor)
def doctor_dashboard(request):
    doctor = request.user
    today = date.today()
    
    appointments = Appointment.objects.filter(
        doctor=doctor,
        date=today,
        status='SCH'
    ).prefetch_related('testrequest_set__testresult').order_by('time_slot')
    
    for appointment in appointments:
        appointment.has_reports = appointment.has_test_reports()
    
    test_results = TestResult.objects.filter(
        test_request__appointment__doctor=doctor,
        test_request__status='COM'
    ).order_by('-completed_at')[:5]
    
    context = {
        'doctor': doctor,
        'appointments': appointments,
        'test_results': test_results,
    }
    return render(request, 'hospital/doctor_dashboard.html', context)

@login_required
@user_passes_test(is_doctor)
def doctor_appointments(request):
    doctor = request.user
    appointments = Appointment.objects.filter(doctor=doctor).order_by('-date', '-time_slot')
    
    context = {
        'doctor': doctor,
        'appointments': appointments,
    }
    return render(request, 'hospital/doctor_appointments.html', context)

@login_required
@user_passes_test(is_doctor)
def doctor_patient_detail(request, patient_id):
    doctor = request.user
    patient = get_object_or_404(Patient, user_id=patient_id)
    
    appointments = Appointment.objects.filter(
        patient=patient,
        doctor=doctor
    ).order_by('-date')
    
    prescriptions = Prescription.objects.filter(
        appointment__patient=patient,
        prescribed_by=doctor
    ).order_by('-prescribed_at')
    
    test_results = TestResult.objects.filter(
        test_request__appointment__patient=patient,
        test_request__requested_by=doctor
    ).order_by('-completed_at')
    
    context = {
        'doctor': doctor,
        'patient': patient,
        'appointments': appointments,
        'prescriptions': prescriptions,
        'test_results': test_results,
    }
    return render(request, 'hospital/doctor_patient_detail.html', context)

@login_required
@user_passes_test(is_doctor)
def request_test(request, appointment_id):
    doctor = request.user
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=doctor)
    
    if request.method == 'POST':
        form = TestRequestForm(request.POST)
        if form.is_valid():
            test_request = form.save(commit=False)
            test_request.appointment = appointment
            test_request.requested_by = doctor
            test_request.save()
            appointment.save()
            messages.success(request, 'Test requested successfully!')
            return redirect('doctor_dashboard')
    else:
        form = TestRequestForm()
    
    context = {
        'doctor': doctor,
        'appointment': appointment,
        'form': form,
    }
    return render(request, 'hospital/request_test.html', context)

@login_required
@user_passes_test(is_doctor)
def create_prescription(request, appointment_id):
    doctor = request.user
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=doctor)
    
    if request.method == 'POST':
        prescription_form = PrescriptionForm(request.POST)
        medicine_form = MedicineForm(request.POST)
        
        if prescription_form.is_valid() and medicine_form.is_valid():
            prescription = prescription_form.save(commit=False)
            prescription.appointment = appointment
            prescription.prescribed_by = doctor
            prescription.save()
            
            medicine = medicine_form.save(commit=False)
            medicine.prescription = prescription
            medicine.save()
            appointment.status = 'COM'
            appointment.save()
            messages.success(request, 'Prescription created successfully!')
            return redirect('doctor_dashboard')
    else:
        prescription_form = PrescriptionForm()
        medicine_form = MedicineForm()
    
    context = {
        'doctor': doctor,
        'appointment': appointment,
        'prescription_form': prescription_form,
        'medicine_form': medicine_form,
    }
    return render(request, 'hospital/create_prescription.html', context)

@login_required
@user_passes_test(is_doctor)
def analyze_test_results(request, appointment_id):
    doctor = request.user
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=doctor)
    test_results = TestResult.objects.filter(
        test_request__appointment=appointment
    ).select_related('test_request__test_type')
    
    abnormal_results = []
    excel_file_url = None
    
    if test_results and test_results[0].file:
        try:
            pdf_path = test_results[0].file.path
            text = extract_text_from_pdf(pdf_path)
            abnormal_results = extract_abnormal_results(text)
            
            if abnormal_results:
                excel_filename = f"abnormal_results_{appointment.id}_{test_results[0].id}.xlsx"
                excel_path = os.path.join(settings.MEDIA_ROOT, 'analysis', excel_filename)
                os.makedirs(os.path.dirname(excel_path), exist_ok=True)
                df = pd.DataFrame(abnormal_results)[["Test", "Status"]]
                df.to_excel(excel_path, index=False)
                excel_file_url = settings.MEDIA_URL + f'analysis/{excel_filename}'
        except Exception as e:
            messages.error(request, f'Failed to analyze PDF: {str(e)}')
    
    if request.method == 'POST':
        messages.success(request, 'Analysis saved successfully!')
        return redirect('doctor_dashboard')
    
    context = {
        'doctor': doctor,
        'appointment': appointment,
        'test_results': test_results,
        'abnormal_results': abnormal_results,
        'excel_file_url': excel_file_url,
    }
    return render(request, 'hospital/analyze_test_results.html', context)

# Receptionist Views
def receptionist_login(request):
    if request.method == 'POST':
        form = ReceptionistLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.get_full_name()}!')
                return redirect('receptionist_dashboard')
    else:
        form = ReceptionistLoginForm()
    return render(request, 'hospital/receptionist_login.html', {'form': form})

@login_required
@user_passes_test(is_receptionist)
def receptionist_dashboard(request):
    today = date.today()
    new_patients = Patient.objects.order_by('-created_at')[:5]
    pending_tests = TestRequest.objects.filter(status='PEN').order_by('-requested_at')
    today_appointments = Appointment.objects.filter(date=today, status='SCH').order_by('time_slot')
    pending_appointments = Appointment.objects.filter(
        status='PEN', 
        doctor__isnull=True
    ).order_by('date')
    
    context = {
        'new_patients': new_patients,
        'pending_tests': pending_tests,
        'today_appointments': today_appointments,
        'pending_appointments': pending_appointments,
    }
    return render(request, 'hospital/receptionist_dashboard.html', context)

@login_required
@user_passes_test(is_receptionist)
def assign_doctor(request, appointment_id):
    appointment = get_object_or_404(
        Appointment, 
        id=appointment_id, 
        status='PEN',
        doctor__isnull=True
    )
    
    if request.method == 'POST':
        doctor_id = request.POST.get('doctor')
        if doctor_id:
            doctor = get_object_or_404(User, id=doctor_id, is_doctor=True)
            appointment.doctor = doctor
            appointment.status = 'SCH'
            appointment.save()
            messages.success(request, f'Doctor {doctor.get_full_name()} assigned successfully!')
            return redirect('receptionist_dashboard')
        else:
            messages.error(request, 'Please select a doctor')
    
    doctors = User.objects.filter(is_doctor=True)
    context = {
        'appointment': appointment,
        'doctors': doctors,
    }
    return render(request, 'hospital/assign_doctor.html', context)

@login_required
@user_passes_test(is_receptionist)
def manage_test_request(request, test_id):
    test_request = get_object_or_404(TestRequest, id=test_id, status='PEN')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            test_request.status = 'APP'
            test_request.approved_by = request.user
            test_request.approved_at = timezone.now()
            test_request.save()
            messages.success(request, 'Test request approved successfully!')
        elif action == 'reject':
            test_request.status = 'REJ'
            test_request.approved_by = request.user
            test_request.approved_at = timezone.now()
            test_request.save()
            messages.success(request, 'Test request rejected.')
        return redirect('receptionist_dashboard')
    
    context = {
        'test_request': test_request,
    }
    return render(request, 'hospital/manage_test_request.html', context)

# Tester Views
def tester_login(request):
    if request.method == 'POST':
        form = TesterLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.get_full_name()}!')
                return redirect('tester_dashboard')
    else:
        form = TesterLoginForm()
    return render(request, 'hospital/tester_login.html', {'form': form})

@login_required
@user_passes_test(is_tester)
def tester_dashboard(request):
    approved_tests = TestRequest.objects.filter(status='APP').order_by('-approved_at')
    
    context = {
        'approved_tests': approved_tests,
    }
    return render(request, 'hospital/tester_dashboard.html', context)

@login_required
@user_passes_test(is_tester)
def upload_test_result(request, test_id):
    test_request = get_object_or_404(TestRequest, id=test_id, status='APP')
    
    if request.method == 'POST':
        form = TestResultForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                test_result = form.save(commit=False)
                test_result.test_request = test_request
                test_result.completed_by = request.user
                test_result.completed_at = timezone.now()
                test_result.save()
                
                test_request.status = 'COM'
                test_request.completed_by = request.user
                test_request.save()
                
                messages.success(request, 'Test results uploaded successfully!')
                return redirect('tester_dashboard')
            except Exception as e:
                messages.error(request, f'Failed to upload test result: {str(e)}')
        else:
            messages.error(request, 'Invalid form data. Please check your inputs.')
    else:
        form = TestResultForm()
    
    context = {
        'test_request': test_request,
        'form': form,
    }
    return render(request, 'hospital/upload_test_result.html', context)