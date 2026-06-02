from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task
def recalculate_reliability_scores():
    """
    Every 6 hours:
    1. Recalculate reliability_score from signal sentiment.
    2. Auto-set is_responsive based on avg_response_minutes.
    3. Auto-set is_community_trusted based on mention_count.
    Note: is_verified and is_featured are NEVER touched here — admin only.
    """
    from apps.businesses.models import Business
    from apps.signals.models import Signal

    updated = 0
    for biz in Business.objects.filter(is_active=True):
        signals  = Signal.objects.filter(business=biz)
        total    = signals.count()
        if total == 0:
            continue

        positive = signals.filter(sentiment='positive').count()
        negative = signals.filter(sentiment='negative').count()

        # Base score: positive ratio
        sentiment_score = int((positive / total) * 100)

        # CallAnchor boost (max +20)
        ca_boost = 0
        if biz.callanchor_enabled and biz.callanchor_score:
            ca_boost = min(int(biz.callanchor_score * 0.2), 20)

        # Negative penalty (max -30)
        neg_penalty = min(negative * 5, 30)

        score = max(0, min(100, sentiment_score + ca_boost - neg_penalty))

        # Auto-compute boolean flags
        is_responsive       = (biz.avg_response_minutes is not None
                               and biz.avg_response_minutes < 45)
        is_community_trusted = biz.mention_count >= 10

        Business.objects.filter(pk=biz.pk).update(
            reliability_score    = score,
            mention_count        = total,
            is_responsive        = is_responsive,
            is_community_trusted = is_community_trusted,
        )
        updated += 1

    logger.info(f'[businesses.tasks] Recalculated {updated} businesses')
    return updated


@shared_task
def approve_business(business_id: int):
    """Mark a business as approved (is_pending_review=False)."""
    from apps.businesses.models import Business
    Business.objects.filter(pk=business_id).update(is_pending_review=False)
    logger.info(f'[businesses.tasks] Approved business {business_id}')


@shared_task
def sync_callanchor_scores():
    """
    Pull response-rate data from CallAnchor API and update
    avg_response_minutes + callanchor_score for enrolled businesses.
    Stub — implement when CallAnchor API key is available.
    """
    from apps.businesses.models import Business
    import requests
    from django.conf import settings

    if not settings.CALLANCHOR_API_KEY:
        logger.warning('[businesses.tasks] CALLANCHOR_API_KEY not set')
        return 0

    businesses = Business.objects.filter(callanchor_enabled=True, is_active=True)
    updated = 0
    for biz in businesses:
        try:
            resp = requests.get(
                f'https://api.callanchor.com/v1/numbers/{biz.callanchor_phone}/score',
                headers={'Authorization': f'Bearer {settings.CALLANCHOR_API_KEY}'},
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json()
                avg_mins = data.get('avg_response_minutes')
                score    = data.get('score')

                update_fields = {}
                if avg_mins is not None:
                    update_fields['avg_response_minutes'] = avg_mins
                    mins = int(avg_mins)
                    if mins < 60:
                        update_fields['avg_response_time'] = f'{mins} min'
                    else:
                        update_fields['avg_response_time'] = f'{mins // 60} hr {mins % 60} min'.strip()
                    update_fields['is_responsive'] = mins < 45
                if score is not None:
                    update_fields['callanchor_score'] = score

                if update_fields:
                    Business.objects.filter(pk=biz.pk).update(**update_fields)
                    updated += 1
        except Exception as e:
            logger.warning(f'[callanchor] Failed for {biz.name}: {e}')

    return updated


@shared_task
def recalculate_single_business(business_id: int):
    """
    Lightweight score recalc for a single business.
    Called immediately after a new review is sentiment-analysed.
    Faster than the full batch job.
    """
    from apps.businesses.models import Business
    from apps.signals.models import Signal
    from apps.reviews.models import Review

    try:
        biz = Business.objects.get(pk=business_id)
    except Business.DoesNotExist:
        return

    # Signal-based score
    signals  = Signal.objects.filter(business=biz)
    sig_total = signals.count()

    if sig_total > 0:
        positive     = signals.filter(sentiment='positive').count()
        negative     = signals.filter(sentiment='negative').count()
        sig_score    = int((positive / sig_total) * 100)
        neg_penalty  = min(negative * 5, 30)
    else:
        sig_score   = 50
        neg_penalty = 0

    # Review-based boost (from direct customer reviews)
    reviews      = Review.objects.filter(business=biz, is_approved=True,
                                         sentiment__in=['positive','neutral','negative'])
    rev_total    = reviews.count()
    if rev_total > 0:
        rev_positive = reviews.filter(sentiment='positive').count()
        rev_score    = int((rev_positive / rev_total) * 100)
        # Weight: 60% signals, 40% direct reviews
        base_score = int(sig_score * 0.6 + rev_score * 0.4)
    else:
        base_score = sig_score

    # CallAnchor boost
    ca_boost = 0
    if biz.callanchor_enabled and biz.callanchor_score:
        ca_boost = min(int(biz.callanchor_score * 0.2), 20)

    score = max(0, min(100, base_score + ca_boost - neg_penalty))

    Business.objects.filter(pk=business_id).update(
        reliability_score    = score,
        mention_count        = sig_total,
        is_responsive        = (biz.avg_response_minutes is not None
                                and biz.avg_response_minutes < 45),
        is_community_trusted = sig_total >= 10,
    )
    logger.info(f'[businesses.tasks] Recalculated single business {business_id}: score={score}')
