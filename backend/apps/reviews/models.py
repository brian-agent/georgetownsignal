from django.db import models
from apps.businesses.models import Business


class Review(models.Model):
    """
    A customer review submitted directly through Georgetown Signal.
    Sentiment is auto-analysed by Gemini 1.5 Flash after submission.
    """

    SOURCE_CHOICES = [
        ('direct',     'Direct Customer Review'),   # submitted via our review form
        ('signal',     'Community Signal'),          # extracted from FB group post
        ('questionnaire', 'Response Questionnaire'), # sent after job completion
        ('callanchor', 'CallAnchor Feedback'),       # via CallAnchor integration
    ]

    SENTIMENT_CHOICES = [
        ('positive', 'Positive'),
        ('neutral',  'Neutral'),
        ('negative', 'Negative'),
        ('pending',  'Pending Analysis'),  # waiting for Gemini
    ]

    business        = models.ForeignKey(
        Business, on_delete=models.CASCADE, related_name='reviews'
    )

    # ── Reviewer info ────────────────────────────────────────────
    author_name     = models.CharField(max_length=100)
    author_email    = models.EmailField(blank=True)  # for questionnaire follow-up
    author_verified = models.BooleanField(
        default=False,
        help_text='True if reviewer confirmed they hired this business.'
    )

    # ── Review content ───────────────────────────────────────────
    text            = models.TextField()
    rating          = models.IntegerField(
        null=True, blank=True,
        help_text='1–5 star rating (optional, from direct reviews and questionnaires)'
    )

    # ── Community quote (for article use) ────────────────────────
    is_featured_quote = models.BooleanField(
        default=False,
        help_text='Admin flags this review as a quotable excerpt for news articles.'
    )
    quote_excerpt   = models.CharField(
        max_length=300, blank=True,
        help_text='Shortened, article-ready version of the review text. '
                  'Auto-populated by Gemini or written by admin.'
    )

    # ── Response quality (for questionnaire path) ────────────────
    response_time_reported = models.IntegerField(
        null=True, blank=True,
        help_text='Minutes to first response, as reported by customer in questionnaire.'
    )
    job_completed   = models.BooleanField(
        null=True, blank=True,
        help_text='Did the provider complete the job? (questionnaire)'
    )

    # ── Sentiment (set by Gemini) ─────────────────────────────────
    sentiment       = models.CharField(
        max_length=20, choices=SENTIMENT_CHOICES, default='pending'
    )
    sentiment_score = models.FloatField(
        null=True, blank=True,
        help_text='Confidence score from Gemini sentiment analysis (0.0–1.0)'
    )
    sentiment_raw   = models.JSONField(
        null=True, blank=True,
        help_text='Raw Gemini response payload for debugging'
    )
    sentiment_analysed_at = models.DateTimeField(null=True, blank=True)

    # ── Meta ──────────────────────────────────────────────────────
    source          = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='direct')
    source_url      = models.URLField(blank=True)
    from_signal     = models.BooleanField(default=False)
    is_approved     = models.BooleanField(
        default=False,
        help_text='Admin approves before review is shown publicly.'
    )
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.author_name} → {self.business.name} ({self.sentiment})'

    @property
    def created_at_display(self):
        from django.utils.timesince import timesince
        return f'{timesince(self.created_at)} ago'

    @property
    def display_text(self):
        """Returns quote_excerpt if set, otherwise truncates text."""
        if self.quote_excerpt:
            return self.quote_excerpt
        return self.text[:200] + ('…' if len(self.text) > 200 else '')


class ResponseQuestionnaire(models.Model):
    """
    Sent to customers after a job is completed.
    Provides the secondary path to is_responsive badge
    when CallAnchor is not installed.
    """
    STATUS_CHOICES = [
        ('sent',      'Sent'),
        ('opened',    'Opened'),
        ('completed', 'Completed'),
        ('expired',   'Expired'),
    ]

    business        = models.ForeignKey(
        Business, on_delete=models.CASCADE, related_name='questionnaires'
    )
    lead            = models.ForeignKey(
        'leads.Lead', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='questionnaires'
    )

    # ── Contact ───────────────────────────────────────────────────
    customer_email  = models.EmailField()
    customer_phone  = models.CharField(max_length=20, blank=True)
    token           = models.CharField(
        max_length=64, unique=True,
        help_text='Secure one-time token in questionnaire link'
    )

    # ── Status ────────────────────────────────────────────────────
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default='sent')
    sent_at         = models.DateTimeField(auto_now_add=True)
    completed_at    = models.DateTimeField(null=True, blank=True)
    expires_at      = models.DateTimeField()

    # ── Responses (populated when customer completes form) ────────
    response_time_minutes = models.IntegerField(
        null=True, blank=True,
        help_text='How many minutes until the provider first responded?'
    )
    job_completed   = models.BooleanField(null=True, blank=True)
    would_recommend = models.BooleanField(null=True, blank=True)
    review_text     = models.TextField(blank=True)
    rating          = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        return f'Questionnaire: {self.business.name} → {self.customer_email} ({self.status})'

    @property
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at
