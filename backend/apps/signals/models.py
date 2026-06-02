from django.db import models
from apps.businesses.models import Business

class Signal(models.Model):
    SENTIMENT = [('positive','Positive'),('neutral','Neutral'),
                 ('negative','Negative'),('request','Request')]
    business      = models.ForeignKey(Business, on_delete=models.SET_NULL,
                                      null=True, blank=True, related_name='signals')
    business_name = models.CharField(max_length=200, blank=True)
    service       = models.CharField(max_length=100)
    mentions      = models.IntegerField(default=1)
    source        = models.CharField(max_length=200)
    source_url    = models.URLField(blank=True)
    raw_text      = models.TextField(blank=True)
    sentiment     = models.CharField(max_length=20, choices=SENTIMENT)
    city          = models.CharField(max_length=100, default='Georgetown')
    state         = models.CharField(max_length=2, default='TX')
    processed     = models.BooleanField(default=False)
    timestamp     = models.DateTimeField()
    created_at    = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ['-timestamp']
    def __str__(self): return f'{self.service} — {self.sentiment}'
