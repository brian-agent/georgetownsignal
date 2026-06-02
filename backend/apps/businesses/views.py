from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Business
from .serializers import BusinessPublicSerializer

# REMOVED: apps.reviews.serializers import ReviewSerializer (and import from models isn't needed here)


class BusinessViewSet(viewsets.ReadOnlyModelViewSet):
    """Public read-only business directory.

    Only active, approved listings are visible.
    """

    queryset = Business.objects.filter(is_active=True, is_pending_review=False)
    serializer_class = BusinessPublicSerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = [
        "category_slug",
        "city",
        "state",
        "is_verified",
        "is_featured",
        "is_responsive",
        "is_community_trusted",
    ]
    search_fields = ["name", "category", "description"]
    ordering_fields = [
        "reliability_score",
        "mention_count",
        "created_at",
        "is_featured",
    ]
    ordering = ["-is_featured", "-reliability_score"]

    def get_queryset(self):
        qs = super().get_queryset()
        limit = self.request.query_params.get("limit")
        if limit:
            try:
                return qs[: int(limit)]
            except ValueError:
                pass
        return qs

    @action(detail=True, methods=["get"], url_path="reviews")
    def reviews(self, request, slug=None):
        # 1. Postpone the import to the moment the endpoint is hit to stop circular loops
        from apps.reviews.models import Review
        from apps.reviews.serializers import ReviewPublicSerializer

        business = self.get_object()

        # 2. Query and serialize using the correct public serializer variant
        qs = Review.objects.filter(business=business).order_by("-created_at")
        return Response(ReviewPublicSerializer(qs, many=True).data)