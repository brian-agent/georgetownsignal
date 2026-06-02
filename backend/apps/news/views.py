from rest_framework import viewsets, filters
from rest_framework.permissions import AllowAny
from .models import NewsPost
from .serializers import NewsPostSerializer
class NewsPostViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NewsPost.objects.filter(is_published=True)
    serializer_class = NewsPostSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title','excerpt','category']
    ordering = ['-published_at']
    def get_queryset(self):
        qs = super().get_queryset()
        limit = self.request.query_params.get('limit')
        if limit:
            try: return qs[:int(limit)]
            except ValueError: pass
        return qs
