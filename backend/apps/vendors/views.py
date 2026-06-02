from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils.text import slugify
from .models import VendorProfile
from .serializers import VendorProfileSerializer, VendorBusinessCreateSerializer
from apps.businesses.models import Business
from apps.businesses.serializers import BusinessVendorSerializer


def get_or_create_vendor(request) -> VendorProfile:
    uid   = request.user.supabase_uid
    email = request.user.email
    vendor, _ = VendorProfile.objects.get_or_create(
        supabase_uid=uid, defaults={'email': email}
    )
    return vendor


class VendorProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        vendor = get_or_create_vendor(request)
        return Response(VendorProfileSerializer(vendor).data)

    def patch(self, request):
        vendor = get_or_create_vendor(request)
        s = VendorProfileSerializer(vendor, data=request.data, partial=True)
        s.is_valid(raise_exception=True)
        s.save()
        return Response(s.data)


class VendorOnboardingView(APIView):
    """Mark onboarding complete after vendor fills profile."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        vendor = get_or_create_vendor(request)
        vendor.onboarding_done = True
        vendor.save()
        return Response({'status': 'onboarding_complete'})


class VendorBusinessListView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        return VendorBusinessCreateSerializer if self.request.method == 'POST' else BusinessVendorSerializer

    def get_queryset(self):
        return Business.objects.filter(supabase_uid=self.request.user.supabase_uid)

    def perform_create(self, serializer):
        name = serializer.validated_data['name']
        slug = slugify(name)
        # ensure unique slug
        base, n = slug, 1
        while Business.objects.filter(slug=slug).exists():
            slug = f'{base}-{n}'; n += 1
        serializer.save(
            supabase_uid     = self.request.user.supabase_uid,
            slug             = slug,
            is_pending_review = True,
            is_verified      = False,
            is_featured      = False,
            is_responsive    = False,
            is_community_trusted = False,
        )


class VendorBusinessView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class   = BusinessVendorSerializer

    def get_queryset(self):
        return Business.objects.filter(supabase_uid=self.request.user.supabase_uid)
