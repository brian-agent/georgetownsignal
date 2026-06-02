from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging
logger = logging.getLogger(__name__)

@shared_task
def aggregate_daily_signals():
    from apps.signals.models import Signal
    from apps.businesses.models import Business
    yesterday = timezone.now() - timedelta(days=1)
    new_sigs = Signal.objects.filter(created_at__gte=yesterday, processed=False)
    counts = {}
    for s in new_sigs:
        if s.business_name:
            counts[s.business_name] = counts.get(s.business_name, 0) + s.mentions
    updated = 0
    for name, count in counts.items():
        for biz in Business.objects.filter(name__icontains=name, is_active=True):
            biz.mention_count += count
            biz.is_community_trusted = biz.mention_count >= 10
            biz.save(update_fields=['mention_count','is_community_trusted','updated_at'])
            updated += 1
    new_sigs.update(processed=True)
    logger.info(f'[signals] Aggregated {new_sigs.count()} signals, updated {updated} businesses')
    return updated
