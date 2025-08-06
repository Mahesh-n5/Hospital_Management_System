from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()

def create_hospital_users():
    # Create groups
    reception_group, _ = Group.objects.get_or_create(name='Receptionists')
    tester_group, _ = Group.objects.get_or_create(name='Testers')

    # Define users (one tester, one receptionist)
    users = [
        {
            'username': 'tester',
            'password': 'Tester@2025',
            'first_name': 'Emma',
            'last_name': 'Wilson',
            'is_tester': True,
            'is_receptionist': False,
            'is_active': True,
            'is_staff': True,
            'group': tester_group
        },
        {
            'username': 'receptionist',
            'password': 'Reception@2025',
            'first_name': 'Liam',
            'last_name': 'Brown',
            'is_tester': False,
            'is_receptionist': True,
            'is_active': True,
            'is_staff': True,
            'group': reception_group
        }
    ]

    # Create or update user accounts
    for user_data in users:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'is_tester': user_data['is_tester'],
                'is_receptionist': user_data['is_receptionist'],
                'is_active': user_data['is_active'],
                'is_staff': user_data['is_staff']
            }
        )
        if created:
            user.set_password(user_data['password'])
            user.save()
            user.groups.add(user_data['group'])
            print(f"Created {user_data['username']}: Username: {user_data['username']} | Password: {user_data['password']}")
        else:
            print(f"{user_data['username']} already exists - updating...")
            user.first_name = user_data['first_name']
            user.last_name = user_data['last_name']
            user.is_tester = user_data['is_tester']
            user.is_receptionist = user_data['is_receptionist']
            user.is_active = user_data['is_active']
            user.is_staff = user_data['is_staff']
            user.set_password(user_data['password'])
            user.save()
            user.groups.clear()
            user.groups.add(user_data['group'])
            print(f"Updated {user_data['username']}: Username: {user_data['username']} | Password: {user_data['password']}")

if __name__ == '__main__':
    create_hospital_users()