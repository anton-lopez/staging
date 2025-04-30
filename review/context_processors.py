from .models import Dorm

def dorms_processor(request):
    """Add dorms to the template context."""
    dorms = Dorm.objects.all().order_by('name')
    return {'dorms': dorms}