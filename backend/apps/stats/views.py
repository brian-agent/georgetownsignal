from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.utils import timezone
from apps.businesses.models import Business
from apps.signals.models import Signal
from apps.leads.models import Lead

class StatsView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0)
        verified = Business.objects.filter(is_verified=True, is_active=True, is_pending_review=False).count()
        signals  = Signal.objects.filter(created_at__gte=month_start).count()
        total    = max(Lead.objects.count(), 1)
        resolved = Lead.objects.filter(status='closed').count()
        return Response({
            'verified_providers': verified,
            'signals_this_month': signals,
            'resolution_rate':    round((resolved / total) * 100),
            'open_requests':      Lead.objects.filter(status__in=['new','notified']).count(),
        })
