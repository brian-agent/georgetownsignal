from django.db import models


class VendorProfile(models.Model):
    """
    One profile per Supabase user.
    Created automatically on first authenticated request (get_or_create pattern).
    """
    supabase_uid    = models.CharField(max_length=36, unique=True, db_index=True)
    email           = models.EmailField()
    full_name       = models.CharField(max_length=200, blank=True)
    phone           = models.CharField(max_length=20, blank=True)
    plan            = models.CharField(
        max_length=20,
        choices=[('free','Free'),('starter','Starter'),('pro','Pro'),('featured','Featured')],
        default='free',
    )
    onboarding_done = models.BooleanField(default=False)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Vendor Profile'

    def __str__(self):
        return f'{self.email} ({self.plan})'
