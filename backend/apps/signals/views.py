from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import Signal
from .serializers import SignalSerializer

class SignalViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Signal.objects.all()
    serializer_class = SignalSerializer
    permission_classes = [AllowAny]

@api_view(['GET'])
@permission_classes([AllowAny])
def ticker_view(request):
    recent = Signal.objects.filter(city='Georgetown').order_by('-timestamp')[:8]
    out = []
    for s in recent:
        name = s.business_name or s.service
        if s.sentiment == 'positive':
            out.append(f'{name} highly recommended this week')
        elif s.sentiment == 'request':
            out.append(f'{s.mentions} Georgetown residents need a {s.service.lower()}')
        else:
            out.append(f'Community signal: {name} · {s.service}')
    if not out:
        out = ['14 Georgetown families needed an electrician this week',
               'Bright Electric mentioned 7 times today',
               'New verified provider added to the directory']
    return Response({'signals': out})
