from django.db import models
from django.utils.text import slugify
import markdown, bleach

class NewsPost(models.Model):
    CATEGORIES   = [('Community','Community'),('Services','Services'),
                    ('Growth','Growth'),('Data','Data Report'),('Warning','Warning')]
    ARTICLE_TYPES = [('service_provider','Service Provider'),('demand_report','Demand Report'),
                     ('community','Community News'),('warning','Consumer Warning'),('local_news','Local News')]

    title                 = models.CharField(max_length=300)
    slug                  = models.SlugField(unique=True, blank=True, max_length=300)
    excerpt               = models.TextField(max_length=500)
    content_md            = models.TextField()
    category              = models.CharField(max_length=50, choices=CATEGORIES)
    article_type          = models.CharField(max_length=30, choices=ARTICLE_TYPES, default='local_news',
                                             help_text='Controls service conversion UI')
    service_category_slug = models.SlugField(blank=True,
                                             help_text='e.g. electricians — links article to provider category')
    tags                  = models.JSONField(default=list)
    read_time_minutes     = models.IntegerField(default=3)
    demand_snapshot       = models.JSONField(null=True, blank=True)
    published_at          = models.DateTimeField()
    is_published          = models.BooleanField(default=False)
    created_at            = models.DateTimeField(auto_now_add=True)

    class Meta: ordering = ['-published_at']
    def __str__(self): return self.title
    def save(self, *args, **kwargs):
        if not self.slug: self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def content_html(self):
        raw = markdown.markdown(self.content_md, extensions=['extra','nl2br'])
        allowed = list(bleach.sanitizer.ALLOWED_TAGS) + [
            'p','h2','h3','h4','ul','ol','li','blockquote','strong','em','a','br','hr']
        return bleach.clean(raw, tags=allowed, strip=True)

    @property
    def is_service_article(self): return self.article_type == 'service_provider'
    @property
    def shows_request_ui(self): return self.article_type in ('service_provider','demand_report','warning')
