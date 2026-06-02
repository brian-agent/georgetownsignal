"""
apps/reviews/tasks.py

Celery tasks for review processing pipeline:
  1. Run Gemini sentiment on new reviews
  2. Process completed questionnaires → update is_responsive
  3. Send questionnaire emails after leads are matched
"""
import secrets
import logging
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def run_sentiment_analysis(self, review_id: int):
    """
    Async Gemini sentiment analysis for a single review.
    Retries up to 3 times on failure (API rate limits etc).
    """
    from apps.reviews.sentiment import analyse_and_save
    try:
        success = analyse_and_save(review_id)
        if not success:
            raise ValueError(f'Sentiment analysis failed for review {review_id}')
    except Exception as exc:
        logger.warning(f'[tasks] Retrying sentiment for review {review_id}: {exc}')
        raise self.retry(exc=exc)


@shared_task
def process_questionnaire_responses():
    """
    Runs hourly. Aggregates completed questionnaire response_time_minutes
    to update business avg_response_minutes when CallAnchor is NOT active.
    This is the fallback path to the is_responsive badge.
    """
    from apps.reviews.models import ResponseQuestionnaire
    from apps.businesses.models import Business

    # Find businesses with completed questionnaires but no CallAnchor
    completed = (
        ResponseQuestionnaire.objects
        .filter(status='completed', response_time_minutes__isnull=False)
        .select_related('business')
    )

    by_business: dict[int, list[int]] = {}
    for q in completed:
        if not q.business.callanchor_enabled:
            by_business.setdefault(q.business_id, []).append(q.response_time_minutes)

    updated = 0
    for biz_id, times in by_business.items():
        avg = int(sum(times) / len(times))
        is_responsive = avg < 45
        # Human-readable string
        if avg < 60:
            display = f'{avg} min'
        else:
            hrs = avg // 60
            mins = avg % 60
            display = f'{hrs} hr {mins} min' if mins else f'{hrs} hr'

        Business.objects.filter(pk=biz_id).update(
            avg_response_minutes = avg,
            avg_response_time    = display,
            is_responsive        = is_responsive,
        )
        updated += 1

    logger.info(f'[questionnaire] Updated {updated} businesses from questionnaire data')
    return updated


@shared_task
def send_review_questionnaire(lead_id: int):
    """
    Called when a lead status changes to 'matched' or 'closed'.
    Sends a review questionnaire to the customer.
    7-day expiry. One questionnaire per lead.
    """
    from apps.leads.models import Lead
    from apps.reviews.models import ResponseQuestionnaire

    if not settings.RESEND_API_KEY:
        logger.warning('[questionnaire] RESEND_API_KEY not set')
        return

    try:
        lead = Lead.objects.get(pk=lead_id)
    except Lead.DoesNotExist:
        return

    if not lead.assigned_to:
        return

    # Don't double-send
    if ResponseQuestionnaire.objects.filter(lead=lead).exists():
        return

    # Extract email from contact field (best effort)
    contact = lead.contact
    if '@' not in contact:
        logger.info(f'[questionnaire] Lead {lead_id} contact is not an email — skipping')
        return

    token = secrets.token_urlsafe(32)
    q = ResponseQuestionnaire.objects.create(
        business       = lead.assigned_to,
        lead           = lead,
        customer_email = contact,
        token          = token,
        expires_at     = timezone.now() + timedelta(days=7),
    )

    review_url = (
        f'{settings.FRONTEND_URL}/review/{token}'
    )

    try:
        import resend
        resend.api_key = settings.RESEND_API_KEY
        resend.Emails.send({
            'from':    settings.DEFAULT_FROM_EMAIL,
            'to':      [contact],
            'subject': f'How did {lead.assigned_to.name} do? — Georgetown Signal',
            'html': f"""
            <div style="max-width:520px;margin:0 auto;font-family:Georgia,serif;">
              <div style="background:#1e4d35;padding:20px;text-align:center;">
                <h1 style="color:#fff;margin:0;font-size:22px;">
                  Georgetown<span style="color:#f0c060;">Signal</span>
                </h1>
              </div>
              <div style="padding:24px;background:#f7f4ef;">
                <h2 style="font-size:20px;color:#1a1208;margin-bottom:8px;">
                  How did your experience go?
                </h2>
                <p style="font-size:14px;color:#555;line-height:1.6;">
                  You recently used <strong>{lead.assigned_to.name}</strong> through
                  Georgetown Signal. We'd love to know how it went — it helps other
                  Georgetown residents find reliable providers.
                </p>
                <p style="font-size:13px;color:#777;">Takes 60 seconds.</p>
                <a href="{review_url}"
                   style="display:inline-block;margin-top:16px;background:#1e4d35;
                          color:#fff;padding:12px 28px;border-radius:24px;
                          text-decoration:none;font-size:14px;">
                  Leave your review →
                </a>
              </div>
              <div style="padding:12px;text-align:center;font-size:11px;color:#aaa;">
                Georgetown Signal · Georgetown, TX ·
                This link expires in 7 days.
              </div>
            </div>
            """,
        })
        q.status = 'sent'
        q.save()
        logger.info(f'[questionnaire] Sent to {contact} for lead {lead_id}')
    except Exception as e:
        logger.error(f'[questionnaire] Send failed: {e}')
