from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Business
from .serializers import BusinessPublicSerializer
from apps.reviews.models import Review
from apps.reviews.serializers import ReviewSerializer


class BusinessViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public read-only business directory.
    Only active, approved listings are visible.
    """
    queryset           = Business.objects.filter(is_active=True, is_pending_review=False)
    serializer_class   = BusinessPublicSerializer
    permission_classes = [AllowAny]
    lookup_field       = 'slug'
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields   = ['category_slug', 'city', 'state',
                          'is_verified', 'is_featured', 'is_responsive', 'is_community_trusted']
    search_fields      = ['name', 'category', 'description']
    ordering_fields    = ['reliability_score', 'mention_count', 'created_at', 'is_featured']
    ordering           = ['-is_featured', '-reliability_score']

    def get_queryset(self):
        qs    = super().get_queryset()
        limit = self.request.query_params.get('limit')
        if limit:
            try:
                return qs[:int(limit)]
            except ValueError:
                pass
        return qs

    @action(detail=True, methods=['get'], url_path='reviews')
    def reviews(self, request, slug=None):
        business = self.get_object()
        qs       = Review.objects.filter(business=business).order_by('-created_at')
        return Response(ReviewSerializer(qs, many=True).data)
