from rest_framework import viewsets, generics, status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.utils import timezone

from .models import Review, ResponseQuestionnaire
from .serializers import (
    ReviewPublicSerializer,
    ReviewSubmitSerializer,
    ArticleQuoteSerializer,
    QuestionnaireSubmitSerializer,
)


class ReviewViewSet(viewsets.ReadOnlyModelViewSet):
    """Public read-only — approved reviews only."""
    queryset           = Review.objects.filter(is_approved=True, sentiment__in=['positive','neutral','negative'])
    serializer_class   = ReviewPublicSerializer
    permission_classes = [AllowAny]
    filterset_fields   = ['business', 'sentiment', 'source', 'is_featured_quote']


class ReviewSubmitView(generics.CreateAPIView):
    """
    POST /api/reviews/submit/
    Any resident can submit a review. It goes through:
      1. Save with sentiment='pending'
      2. Celery queues Gemini sentiment analysis
      3. Admin approves (or auto-approved if sentiment is positive)
    """
    serializer_class   = ReviewSubmitSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        review = serializer.save(
            sentiment   = 'pending',
            source      = 'direct',
            is_approved = False,   # admin approval gate
        )
        # Queue Gemini sentiment analysis
        from apps.reviews.tasks import run_sentiment_analysis
        run_sentiment_analysis.delay(review.id)

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        return Response(
            {'status': 'submitted',
             'message': 'Thank you! Your review is being processed and will appear shortly.'},
            status=status.HTTP_201_CREATED,
        )


class ArticleQuoteView(APIView):
    """
    GET /api/reviews/article-quote/?business_slug=bright-electric
    Returns the single best featured quote for embedding in a news article.
    Falls back to the highest-scoring positive review if no featured quote exists.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        slug = request.query_params.get('business_slug')
        if not slug:
            return Response({'error': 'business_slug required'}, status=400)

        # First: admin-flagged featured quote
        review = (
            Review.objects
            .filter(business__slug=slug, is_featured_quote=True,
                    is_approved=True, quote_excerpt__gt='')
            .first()
        )
        # Fallback: highest-confidence positive review with a quote
        if not review:
            review = (
                Review.objects
                .filter(business__slug=slug, sentiment='positive',
                        is_approved=True, quote_excerpt__gt='')
                .order_by('-sentiment_score')
                .first()
            )

        if not review:
            return Response(None)

        return Response(ArticleQuoteSerializer(review).data)


class QuestionnaireView(APIView):
    """
    GET  /api/reviews/questionnaire/{token}/  → fetch questionnaire details
    POST /api/reviews/questionnaire/{token}/  → submit responses
    """
    permission_classes = [AllowAny]

    def get(self, request, token):
        try:
            q = ResponseQuestionnaire.objects.select_related('business').get(token=token)
        except ResponseQuestionnaire.DoesNotExist:
            return Response({'error': 'Invalid or expired link.'}, status=404)

        if q.is_expired or q.status == 'expired':
            return Response({'error': 'This review link has expired.'}, status=410)

        if q.status == 'completed':
            return Response({'error': 'Already submitted.'}, status=409)

        # Mark as opened
        if q.status == 'sent':
            q.status = 'opened'
            q.save(update_fields=['status'])

        return Response({
            'business_name': q.business.name,
            'category':      q.business.category,
        })

    def post(self, request, token):
        try:
            q = ResponseQuestionnaire.objects.select_related('business').get(token=token)
        except ResponseQuestionnaire.DoesNotExist:
            return Response({'error': 'Invalid link.'}, status=404)

        if q.is_expired:
            return Response({'error': 'This link has expired.'}, status=410)

        if q.status == 'completed':
            return Response({'error': 'Already submitted.'}, status=409)

        s = QuestionnaireSubmitSerializer(q, data=request.data, partial=True)
        s.is_valid(raise_exception=True)
        q = s.save(status='completed', completed_at=timezone.now())

        # Create a Review from questionnaire data if they left text
        if q.review_text:
            review = Review.objects.create(
                business               = q.business,
                author_name            = 'Verified Customer',
                author_email           = q.customer_email,
                author_verified        = True,
                text                   = q.review_text,
                rating                 = q.rating,
                response_time_reported = q.response_time_minutes,
                job_completed          = q.job_completed,
                source                 = 'questionnaire',
                sentiment              = 'pending',
                is_approved            = False,
            )
            from apps.reviews.tasks import run_sentiment_analysis
            run_sentiment_analysis.delay(review.id)

        # Trigger questionnaire aggregation for is_responsive update
        from apps.reviews.tasks import process_questionnaire_responses
        process_questionnaire_responses.delay()

        return Response({
            'status': 'completed',
            'message': 'Thank you for your feedback! It helps Georgetown residents find reliable providers.',
        })
