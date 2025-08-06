from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    is_doctor = models.BooleanField(default=False)
    is_receptionist = models.BooleanField(default=False)
    is_tester = models.BooleanField(default=False)
    is_patient = models.BooleanField(default=False)
    specialty = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    
    def __str__(self):
        return self.get_full_name() or self.username

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    date_of_birth = models.DateField()
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    address = models.TextField()
    blood_group = models.CharField(max_length=5, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} (ID: {self.user_id})"

class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        limit_choices_to={'is_doctor': True},
        null=True,
        blank=True
    )
    date = models.DateField()
    TIME_SLOTS = [
        ('09:00', '9:00 AM'),
        ('10:00', '10:00 AM'),
        ('11:00', '11:00 AM'),
        ('12:00', '12:00 PM'),
        ('14:00', '2:00 PM'),
        ('15:00', '3:00 PM'),
        ('16:00', '4:00 PM'),
    ]
    time_slot = models.CharField(max_length=5, choices=TIME_SLOTS)
    problem = models.TextField()
    STATUS_CHOICES = [
        ('PEN', 'Pending'),
        ('SCH', 'Scheduled'),
        ('COM', 'Completed'),
        ('CAN', 'Cancelled'),
    ]
    status = models.CharField(max_length=3, choices=STATUS_CHOICES, default='PEN')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date', 'time_slot']
    
    def __str__(self):
        doctor_name = self.doctor.get_full_name() if self.doctor else "Unassigned"
        return f"{self.patient} with Dr. {doctor_name} on {self.date} at {self.get_time_slot_display()}"
    
    def has_test_reports(self):
        return self.testrequest_set.filter(testresult__isnull=False).exists()

class TestType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    
    def __str__(self):
        return self.name

class TestRequest(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    test_type = models.ForeignKey(TestType, on_delete=models.CASCADE)
    notes = models.TextField(blank=True)
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requested_tests')
    requested_at = models.DateTimeField(auto_now_add=True)
    STATUS_CHOICES = [
        ('PEN', 'Pending Approval'),
        ('APP', 'Approved'),
        ('REJ', 'Rejected'),
        ('COL', 'Sample Collected'),
        ('PRO', 'In Progress'),
        ('COM', 'Completed'),
        ('CAN', 'Cancelled'),
    ]
    status = models.CharField(max_length=3, choices=STATUS_CHOICES, default='PEN')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_tests')
    approved_at = models.DateTimeField(null=True, blank=True)
    completed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='completed_tests')
    
    class Meta:
        ordering = ['-requested_at']
    
    def __str__(self):
        return f"{self.test_type} for {self.appointment.patient}"
    
    def has_results(self):
        return hasattr(self, 'testresult') and self.testresult is not None

class TestResult(models.Model):
    test_request = models.OneToOneField(TestRequest, on_delete=models.CASCADE)
    result = models.TextField()
    file = models.FileField(upload_to='test_results/%Y/%m/%d/', blank=True, null=True)
    completed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Results for {self.test_request}"

class Prescription(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    prescribed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    prescribed_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-prescribed_at']
    
    def __str__(self):
        return f"Prescription for {self.appointment.patient} by Dr. {self.prescribed_by}"

class Medicine(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='medicines')
    name = models.CharField(max_length=100)
    dosage = models.CharField(max_length=50)
    duration = models.CharField(max_length=50)
    instructions = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.name} - {self.dosage} for {self.duration}"