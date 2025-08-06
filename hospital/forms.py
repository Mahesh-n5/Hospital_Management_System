from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import (
    User, Patient, Appointment, TestType, 
    TestRequest, TestResult, Prescription, Medicine
)

class PatientSignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(max_length=254, required=True)
    phone_number = forms.CharField(max_length=15, required=True)
    date_of_birth = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date'}))
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=True)
    address = forms.CharField(widget=forms.Textarea, required=True)
    blood_group = forms.CharField(max_length=5, required=False)
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone_number', 
                 'password1', 'password2', 'date_of_birth', 'gender', 'address', 'blood_group')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_patient = True
        if commit:
            user.save()
            Patient.objects.create(
                user=user,
                date_of_birth=self.cleaned_data['date_of_birth'],
                gender=self.cleaned_data['gender'],
                address=self.cleaned_data['address'],
                blood_group=self.cleaned_data['blood_group']
            )
        return user

class DoctorSignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(max_length=254, required=True)
    phone_number = forms.CharField(max_length=15, required=True)
    specialty = forms.CharField(max_length=100, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone_number', 
                 'specialty', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_doctor = True
        user.specialty = self.cleaned_data['specialty']
        if commit:
            user.save()
        return user


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['date', 'time_slot', 'problem']  # Remove doctor field
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'problem': forms.Textarea(attrs={'rows': 3}),
        }
    
    

class TestRequestForm(forms.ModelForm):
    class Meta:
        model = TestRequest
        fields = ['test_type', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class TestResultForm(forms.ModelForm):
    class Meta:
        model = TestResult
        fields = ['result', 'file', 'notes']
        widgets = {
            'result': forms.Textarea(attrs={'rows': 5}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = ['name', 'dosage', 'duration', 'instructions']
        widgets = {
            'instructions': forms.Textarea(attrs={'rows': 2}),
        }

class PatientLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    
    def confirm_login_allowed(self, user):
        if not user.is_patient:
            raise forms.ValidationError("This account is not a patient account.", code='invalid_login')

class DoctorLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    
    def confirm_login_allowed(self, user):
        if not user.is_doctor:
            raise forms.ValidationError("This account is not a doctor account.", code='invalid_login')

class ReceptionistLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    
    def confirm_login_allowed(self, user):
        if not user.is_receptionist:
            raise forms.ValidationError("This account is not a receptionist account.", code='invalid_login')

class TesterLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    
    def confirm_login_allowed(self, user):
        if not user.is_tester:
            raise forms.ValidationError("This account is not a tester account.", code='invalid_login')