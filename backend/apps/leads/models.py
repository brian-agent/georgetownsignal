from django.db import models
class Lead(models.Model):
    URGENCY = [('normal','Normal'),('urgent','Urgent'),('emergency','Emergency')]
    STATUS  = [('new','New'),('notified','Notified'),('matched','Matched'),('closed','Closed')]
    category    = models.CharField(max_length=100)
    description = models.TextField()
    budget      = models.CharField(max_length=100, blank=True)
    contact     = models.CharField(max_length=200)
    urgency     = models.CharField(max_length=20, choices=URGENCY, default='normal')
    city        = models.CharField(max_length=100, default='Georgetown')
    state       = models.CharField(max_length=2, default='TX')
    status      = models.CharField(max_length=20, choices=STATUS, default='new')
    assigned_to = models.ForeignKey('businesses.Business', on_delete=models.SET_NULL,
                                    null=True, blank=True, related_name='leads')
    created_at  = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ['-created_at']
