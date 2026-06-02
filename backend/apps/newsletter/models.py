from django.db import models
class Subscriber(models.Model):
    email      = models.EmailField(unique=True)
    city       = models.CharField(max_length=100, default='Georgetown')
    state      = models.CharField(max_length=2, default='TX')
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.email
