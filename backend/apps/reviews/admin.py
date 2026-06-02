from django.contrib import admin
from django.utils.html import format_html
from .models import Review, ResponseQuestionnaire


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'author_name', 'business', 'sentiment_badge', 'sentiment_score',
        'source', 'rating', 'is_featured_quote', 'is_approved', 'created_at',
    )
    list_filter  = ('sentiment', 'source', 'is_approved', 'is_featured_quote',
                    'author_verified')
    search_fields = ('author_name', 'text', 'business__name')
    readonly_fields = ('sentiment', 'sentiment_score', 'sentiment_raw',
                       'sentiment_analysed_at', 'created_at', 'updated_at')
    actions = ['approve_reviews', 'flag_as_featured_quote', 'rerun_sentiment']

    fieldsets = (
        ('Review', {
            'fields': ('business', 'author_name', 'author_email', 'author_verified',
                       'rating', 'text', 'source', 'source_url'),
        }),
        ('Article Quote', {
            'fields': ('is_featured_quote', 'quote_excerpt'),
            'description': 'Flag this review and set a short excerpt for embedding in news articles.',
        }),
        ('Response Data', {
            'fields': ('response_time_reported', 'job_completed'),
            'classes': ('collapse',),
        }),
        ('Sentiment (Gemini)', {
            'fields': ('sentiment', 'sentiment_score', 'sentiment_analysed_at', 'sentiment_raw'),
            'classes': ('collapse',),
        }),
        ('Status', {
            'fields': ('is_approved',),
        }),
    )

    def sentiment_badge(self, obj):
        colors = {
            'positive': ('#0F6E56', '#E1F5EE'),
            'neutral':  ('#555',    '#f0f0f0'),
            'negative': ('#A32D2D', '#FCEBEB'),
            'pending':  ('#633806', '#FAEEDA'),
        }
        fg, bg = colors.get(obj.sentiment, ('#333', '#eee'))
        return format_html(
            '<span style="background:{};color:{};padding:2px 8px;border-radius:10px;font-size:11px;">{}</span>',
            bg, fg, obj.sentiment,
        )
    sentiment_badge.short_description = 'Sentiment'

    @admin.action(description='✅ Approve selected reviews')
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)

    @admin.action(description='💬 Flag as featured article quote')
    def flag_as_featured_quote(self, request, queryset):
        queryset.update(is_featured_quote=True)

    @admin.action(description='🔄 Re-run Gemini sentiment analysis')
    def rerun_sentiment(self, request, queryset):
        from apps.reviews.tasks import run_sentiment_analysis
        for review in queryset:
            run_sentiment_analysis.delay(review.id)
        self.message_user(request, f'Queued sentiment analysis for {queryset.count()} reviews.')


@admin.register(ResponseQuestionnaire)
class QuestionnaireAdmin(admin.ModelAdmin):
    list_display = ('business', 'customer_email', 'status',
                    'response_time_minutes', 'job_completed', 'sent_at')
    list_filter  = ('status', 'job_completed', 'would_recommend')
    search_fields = ('business__name', 'customer_email')
    readonly_fields = ('token', 'sent_at', 'completed_at', 'expires_at')
