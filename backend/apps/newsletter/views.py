from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import Subscriber
class SubscribeView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get('email','').strip().lower()
        if not email or '@' not in email:
            return Response({'error':'Valid email required'}, status=400)
        sub, created = Subscriber.objects.get_or_create(
            email=email, defaults={'city': request.data.get('city','Georgetown'),
                                   'state': request.data.get('state','TX')})
        if not created:
            sub.is_active = True; sub.save()
        return Response({'status':'subscribed','created':created}, status=201)
