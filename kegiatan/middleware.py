from django.utils.timezone import now
from .models import VisitorCount

class VisitorCountMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.method == "GET" and not request.path.startswith(("/static", "/admin")):
            today = now().date()
            visitor_count, _ = VisitorCount.objects.get_or_create(id=1)

            # reset harian jika sudah ganti tanggal
            if visitor_count.last_reset != today:
                visitor_count.count = 0
                visitor_count.last_reset = today

            # tambah kunjungan hari ini & total
            visitor_count.count += 1
            visitor_count.total_count += 1
            visitor_count.save()

        return response
