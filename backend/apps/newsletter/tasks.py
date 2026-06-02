from celery import shared_task
from django.conf import settings
from django.utils import timezone
import logging
logger = logging.getLogger(__name__)

@shared_task
def send_weekly_newsletter():
    if not settings.RESEND_API_KEY:
        logger.warning('[newsletter] RESEND_API_KEY not set'); return 0
    from apps.newsletter.models import Subscriber
    from apps.businesses.models import Business
    import resend
    resend.api_key = settings.RESEND_API_KEY
    top = Business.objects.filter(is_active=True, is_pending_review=False,
                                  is_verified=True).order_by('-reliability_score')[:5]
    rows = ''.join([f'<tr><td style="padding:6px 0;border-bottom:1px solid #d4c9b5;">'
                    f'<strong>{i+1}. {b.name}</strong><br>'
                    f'<small style="color:#666;">{b.category} · {b.reliability_score}% · {b.avg_response_time}</small></td></tr>'
                    for i,b in enumerate(top)])
    html = f"""<div style="max-width:560px;margin:0 auto;font-family:Georgia,serif;">
      <div style="background:#1e4d35;padding:24px;text-align:center;">
        <h1 style="color:#fff;margin:0;">Georgetown<span style="color:#f0c060;">Signal</span></h1>
        <p style="color:rgba(255,255,255,.5);font-size:12px;margin:6px 0 0;font-family:sans-serif;">
          WEEKLY INTELLIGENCE · {timezone.now().strftime('%B %d, %Y')} · GEORGETOWN TX</p>
      </div>
      <div style="padding:24px;background:#f7f4ef;">
        <h2 style="border-bottom:2px solid #1e4d35;padding-bottom:6px;color:#1e4d35;font-size:16px;">Most trusted providers</h2>
        <table style="width:100%;border-collapse:collapse;">{rows}</table>
        <div style="text-align:center;margin-top:20px;">
          <a href="https://georgetownsignal.com/request"
             style="background:#1e4d35;color:#fff;padding:10px 24px;border-radius:20px;text-decoration:none;font-size:13px;">
            Submit a service request →</a>
        </div>
      </div>
    </div>"""
    subs = Subscriber.objects.filter(is_active=True)
    sent = 0
    for sub in subs:
        try:
            resend.Emails.send({'from': settings.DEFAULT_FROM_EMAIL, 'to': [sub.email],
                                'subject': f'Georgetown Signal Weekly — {timezone.now().strftime("%B %d")}',
                                'html': html})
            sent += 1
        except Exception as e:
            logger.warning(f'[newsletter] {sub.email}: {e}')
    return sent
