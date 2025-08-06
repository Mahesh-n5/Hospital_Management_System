from django.contrib.auth import get_user_model
from hospital.models import TestType

def create_test_types():
    test_types = [
        {
            'name': 'Blood Test',
            'description': 'Complete blood count (CBC) to evaluate overall health.',
            'price': 50.00
        },
        {
            'name': 'Urine Test',
            'description': 'Urinalysis to detect urinary tract infections or kidney issues.',
            'price': 30.00
        },
        {
            'name': 'X-Ray',
            'description': 'Radiographic imaging to diagnose bone fractures or lung conditions.',
            'price': 100.00
        },
        {
            'name': 'ECG',
            'description': 'Electrocardiogram to monitor heart activity.',
            'price': 75.00
        },
        {
            'name': 'Ultrasound',
            'description': 'Imaging to examine organs or monitor pregnancy.',
            'price': 120.00
        },
        {
            'name': 'MRI Scan',
            'description': 'Magnetic resonance imaging for detailed organ and tissue visualization.',
            'price': 300.00
        },
        {
            'name': 'CT Scan',
            'description': 'Computed tomography for cross-sectional body imaging.',
            'price': 250.00
        },
        {
            'name': 'Lipid Profile',
            'description': 'Blood test to measure cholesterol and triglyceride levels.',
            'price': 60.00
        },
        {
            'name': 'Thyroid Function Test',
            'description': 'Blood test to assess thyroid hormone levels.',
            'price': 80.00
        },
        {
            'name': 'Blood Glucose Test',
            'description': 'Test to measure blood sugar levels for diabetes monitoring.',
            'price': 40.00
        }
    ]

    for test in test_types:
        test_type, created = TestType.objects.get_or_create(
            name=test['name'],
            defaults={
                'description': test['description'],
                'price': test['price']
            }
        )
        if created:
            print(f"Created test type: {test['name']} | Price: ${test['price']}")
        else:
            print(f"Test type {test['name']} already exists - updating...")
            test_type.description = test['description']
            test_type.price = test['price']
            test_type.save()
            print(f"Updated test type: {test['name']} | Price: ${test['price']}")

if __name__ == '__main__':
    create_test_types()