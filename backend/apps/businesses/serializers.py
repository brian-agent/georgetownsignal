from rest_framework import serializers
from .models import Business


class BusinessPublicSerializer(serializers.ModelSerializer):
    """Read-only serializer for public directory pages."""
    badges = serializers.SerializerMethodField()

    class Meta:
        model  = Business
        fields = [
            'id', 'name', 'slug', 'category', 'category_slug',
            'description', 'phone', 'website', 'address', 'city', 'state',
            # Trust flags
            'is_verified', 'is_featured', 'is_responsive', 'is_community_trusted',
            # Computed
            'reliability_score', 'avg_response_time', 'mention_count',
            'jobs_completed', 'badges',
            'created_at',
        ]
        read_only_fields = fields

    def get_badges(self, obj):
        return obj.badges


class BusinessVendorSerializer(serializers.ModelSerializer):
    """
    Vendor-facing serializer.
    Vendors can write core info fields only.
    Trust flags and metrics are read-only (set by admin/Celery).
    """
    badges = serializers.SerializerMethodField()

    class Meta:
        model  = Business
        fields = [
            'id', 'name', 'slug', 'category', 'category_slug',
            'description', 'phone', 'website', 'address', 'city', 'state',
            'callanchor_enabled', 'callanchor_phone',
            # Read-only trust
            'is_verified', 'is_featured', 'is_responsive', 'is_community_trusted',
            'reliability_score', 'avg_response_time', 'mention_count',
            'jobs_completed', 'badges',
            # Status
            'is_active', 'is_pending_review', 'rejection_reason',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'slug', 'is_verified', 'is_featured', 'is_responsive',
            'is_community_trusted', 'reliability_score', 'avg_response_time',
            'mention_count', 'jobs_completed', 'badges',
            'is_pending_review', 'rejection_reason',
            'created_at', 'updated_at',
        ]

    def get_badges(self, obj):
        return obj.badges


class BusinessAdminSerializer(serializers.ModelSerializer):
    """Full serializer for admin operations (all fields writable)."""
    badges = serializers.SerializerMethodField()

    class Meta:
        model  = Business
        fields = '__all__'

    def get_badges(self, obj):
        return obj.badges
