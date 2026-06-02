from rest_framework import serializers
from .models import VendorProfile
from apps.businesses.models import Business
from apps.businesses.serializers import BusinessVendorSerializer


class VendorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model  = VendorProfile
        fields = ['id', 'email', 'full_name', 'phone', 'plan',
                  'onboarding_done', 'created_at', 'updated_at']
        read_only_fields = ['id', 'email', 'plan', 'created_at', 'updated_at']


class VendorBusinessCreateSerializer(serializers.ModelSerializer):
    """
    Used when a vendor submits a new listing.
    Trust flags and metrics are excluded — set by admin/Celery only.
    """
    class Meta:
        model  = Business
        fields = [
            'name', 'category', 'category_slug',
            'description', 'phone', 'website', 'address', 'city', 'state',
            'callanchor_enabled', 'callanchor_phone',
        ]

    def validate_category_slug(self, value):
        allowed = [
            'electricians', 'plumbers', 'roofers', 'hvac',
            'cleaners', 'movers', 'painters', 'landscapers',
        ]
        if value not in allowed:
            raise serializers.ValidationError(
                f'category_slug must be one of: {", ".join(allowed)}'
            )
        return value
