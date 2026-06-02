from rest_framework import serializers, generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.conf import settings
from .models import Lead
from apps.businesses.models import Business

class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Lead
        fields = ['category','description','budget','contact','urgency','city','state']

class LeadCreateView(generics.CreateAPIView):
    serializer_class   = LeadSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)
        lead = s.save()
        self._notify(lead)
        return Response({'status':'ok','id':lead.id}, status=status.HTTP_201_CREATED)

    def _notify(self, lead):
        if not settings.RESEND_API_KEY: return
        try:
            import resend
            resend.api_key = settings.RESEND_API_KEY
            providers = Business.objects.filter(
                category_slug=lead.category.lower(),
                is_verified=True, is_active=True, is_pending_review=False
            )[:5]
            for p in providers:
                resend.Emails.send({
                    'from': settings.DEFAULT_FROM_EMAIL,
                    'to':   [f'{p.name} <noreply@georgetownsignal.com>'],
                    'subject': f'New {lead.category} request — Georgetown TX',
                    'html': (f'<p><strong>Job:</strong> {lead.description}</p>'
                             f'<p><strong>Budget:</strong> {lead.budget or "Not specified"}</p>'
                             f'<p><strong>Urgency:</strong> {lead.urgency}</p>'
                             f'<p><strong>Contact:</strong> {lead.contact}</p>'),
                })
        except Exception as e:
            print(f'[leads] notify error: {e}')
