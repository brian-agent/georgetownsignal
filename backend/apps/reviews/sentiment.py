"""
apps/reviews/sentiment.py

Gemini 1.5 Flash sentiment analysis for customer reviews.
Cheapest capable LLM at this volume — essentially free for <100 reviews/day.

Gemini 1.5 Flash pricing (as of 2025):
  Input:  $0.075 per 1M tokens
  Output: $0.30 per 1M tokens
  A 200-word review costs ~$0.000015 to analyse. 1,000 reviews = $0.015.
"""

import json
import logging
from typing import Optional
from django.conf import settings

logger = logging.getLogger(__name__)


SENTIMENT_PROMPT = """
You are a sentiment analysis engine for Georgetown Signal, a local service directory.

Analyse the following customer review of a local home service provider.

Return ONLY valid JSON in this exact format:
{
  "sentiment": "positive" | "neutral" | "negative",
  "score": 0.0-1.0,
  "reasoning": "one sentence explanation",
  "quote_excerpt": "the single most quotable sentence from the review (max 150 chars, exact words from review)",
  "response_quality": "fast" | "slow" | "unknown",
  "would_recommend": true | false | null
}

Rules:
- sentiment score: 1.0 = strongly positive, 0.5 = neutral, 0.0 = strongly negative
- quote_excerpt must be verbatim text from the review, suitable for publishing on the website
- response_quality: "fast" if they mention quick response/arrival, "slow" if they complain about wait times
- would_recommend: true/false if mentioned, null if unclear

Review text:
\"\"\"
{review_text}
\"\"\"
"""


def analyse_sentiment(review_text: str) -> Optional[dict]:
    """
    Calls Gemini 1.5 Flash to analyse review sentiment.
    Returns structured dict or None on failure.
    """
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        logger.warning('[sentiment] GEMINI_API_KEY not configured — skipping analysis')
        return None

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)

        model    = genai.GenerativeModel('gemini-1.5-flash')
        prompt   = SENTIMENT_PROMPT.format(review_text=review_text[:2000])
        response = model.generate_content(
            prompt,
            generation_config={
                'temperature':     0.1,   # low temp = consistent JSON
                'max_output_tokens': 300,
                'response_mime_type': 'application/json',
            }
        )

        raw  = response.text.strip()
        data = json.loads(raw)

        # Validate required fields
        assert data.get('sentiment') in ('positive', 'neutral', 'negative')
        assert isinstance(data.get('score'), (int, float))

        logger.info(
            f'[sentiment] Analysed review: {data["sentiment"]} '
            f'(score={data["score"]:.2f})'
        )
        return data

    except json.JSONDecodeError as e:
        logger.error(f'[sentiment] JSON parse error: {e}')
    except AssertionError:
        logger.error('[sentiment] Invalid response structure from Gemini')
    except Exception as e:
        logger.error(f'[sentiment] Gemini API error: {e}')

    return None


def analyse_and_save(review_id: int) -> bool:
    """
    Fetch a Review by ID, run Gemini analysis, save results back.
    Designed to be called from a Celery task.
    """
    from apps.reviews.models import Review
    from django.utils import timezone

    try:
        review = Review.objects.get(pk=review_id)
    except Review.DoesNotExist:
        logger.error(f'[sentiment] Review {review_id} not found')
        return False

    result = analyse_sentiment(review.text)
    if not result:
        return False

    review.sentiment              = result['sentiment']
    review.sentiment_score        = result.get('score')
    review.sentiment_raw          = result
    review.sentiment_analysed_at  = timezone.now()

    # Auto-populate quote_excerpt if Gemini extracted one and none exists
    if not review.quote_excerpt and result.get('quote_excerpt'):
        review.quote_excerpt = result['quote_excerpt']

    review.save(update_fields=[
        'sentiment', 'sentiment_score', 'sentiment_raw',
        'sentiment_analysed_at', 'quote_excerpt', 'updated_at',
    ])

    # Update business reliability score after new sentiment data
    from apps.businesses.tasks import recalculate_single_business
    recalculate_single_business.delay(review.business_id)

    logger.info(f'[sentiment] Review {review_id} saved: {review.sentiment}')
    return True
