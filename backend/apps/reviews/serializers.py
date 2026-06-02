from rest_framework import serializers
from .models import Review, ResponseQuestionnaire


class ReviewPublicSerializer(serializers.ModelSerializer):
    """Shown on public business pages — approved reviews only."""
    created_at_display = serializers.CharField(read_only=True)
    display_text       = serializers.CharField(read_only=True)

    class Meta:
        model  = Review
        fields = [
            'id', 'author_name', 'rating', 'text', 'display_text',
            'sentiment', 'sentiment_score',
            'source', 'is_featured_quote', 'quote_excerpt',
            'created_at_display',
        ]
        # Never expose author_email publicly
        read_only_fields = fields


class ReviewSubmitSerializer(serializers.ModelSerializer):
    """
    Used by residents to submit a direct review.
    Fields are minimal — sentiment is filled in by Gemini async.
    """
    class Meta:
        model  = Review
        fields = [
            'business', 'author_name', 'author_email',
            'text', 'rating',
            'response_time_reported', 'job_completed',
        ]

    def validate_rating(self, value):
        if value is not None and not (1 <= value <= 5):
            raise serializers.ValidationError('Rating must be between 1 and 5.')
        return value

    def validate_text(self, value):
        if len(value.strip()) < 20:
            raise serializers.ValidationError('Review must be at least 20 characters.')
        return value.strip()


class ArticleQuoteSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for embedding a featured quote inside a news article.
    Used by the news article page to fetch the best quote for a business.
    """
    class Meta:
        model  = Review
        fields = ['author_name', 'quote_excerpt', 'source', 'created_at_display']
        read_only_fields = fields


class QuestionnaireSubmitSerializer(serializers.ModelSerializer):
    """Customer completes the questionnaire via the token link."""
    class Meta:
        model  = ResponseQuestionnaire
        fields = [
            'response_time_minutes', 'job_completed',
            'would_recommend', 'review_text', 'rating',
        ]

    def validate_rating(self, value):
        if value is not None and not (1 <= value <= 5):
            raise serializers.ValidationError('Rating must be between 1 and 5.')
        return value
