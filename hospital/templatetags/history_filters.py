from django import template

register = template.Library()

@register.filter
def filter_by_appointment(queryset, appointment):
    """
    Filter test results or prescriptions by appointment.
    """
    if queryset.model.__name__ == 'TestResult':
        return queryset.filter(test_request__appointment=appointment)
    elif queryset.model.__name__ == 'Prescription':
        return queryset.filter(appointment=appointment)
    return queryset