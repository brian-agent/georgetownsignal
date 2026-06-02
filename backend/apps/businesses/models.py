from django.db import models
from django.utils.text import slugify


class Business(models.Model):

    # ── Ownership (Supabase UID — no Django FK to auth) ─────────
    supabase_uid        = models.CharField(max_length=36, blank=True, db_index=True)

    # ── Core info ────────────────────────────────────────────────
    name                = models.CharField(max_length=200)
    slug                = models.SlugField(unique=True, blank=True)
    category            = models.CharField(max_length=100)
    category_slug       = models.SlugField(max_length=100)
    description         = models.TextField(blank=True)
    phone               = models.CharField(max_length=20, blank=True)
    website             = models.URLField(blank=True)
    address             = models.CharField(max_length=300, blank=True)
    city                = models.CharField(max_length=100, default='Georgetown')
    state               = models.CharField(max_length=2, default='TX')

    # ── Explicit trust flags (admin-set or auto-computed) ────────
    is_verified         = models.BooleanField(
        default=False,
        help_text='Admin grants after manual vetting. Unlocks Signal Verified badge.',
    )
    is_featured         = models.BooleanField(
        default=False,
        help_text='Paid upgrade. Shows Featured badge and top placement.',
    )
    is_responsive       = models.BooleanField(
        default=False,
        help_text='Auto-set when avg_response_minutes < 45. Shows Fastest Responder badge.',
    )
    is_community_trusted = models.BooleanField(
        default=False,
        help_text='Auto-set when mention_count >= 10. Shows Community Trusted badge.',
    )

    # ── Computed trust metrics (updated by Celery) ───────────────
    reliability_score   = models.IntegerField(default=0)
    avg_response_minutes = models.IntegerField(null=True, blank=True)
    avg_response_time   = models.CharField(max_length=50, default='—')
    mention_count       = models.IntegerField(default=0)
    jobs_completed      = models.IntegerField(default=0)

    # ── CallAnchor ───────────────────────────────────────────────
    callanchor_enabled  = models.BooleanField(default=False)
    callanchor_phone    = models.CharField(max_length=20, blank=True)
    callanchor_score    = models.IntegerField(null=True, blank=True)

    # ── Listing status ───────────────────────────────────────────
    is_active           = models.BooleanField(default=True)
    is_pending_review   = models.BooleanField(
        default=True,
        help_text='New vendor submissions await admin approval before going public.',
    )
    rejection_reason    = models.TextField(blank=True)

    created_at          = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)

    class Meta:
        ordering         = ['-is_featured', '-reliability_score']
        verbose_name_plural = 'businesses'

    def __str__(self):
        return f'{self.name} ({self.city}, {self.state})'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        # Auto-compute boolean flags from metrics before save
        if self.avg_response_minutes is not None:
            self.is_responsive = self.avg_response_minutes < 45
        self.is_community_trusted = self.mention_count >= 10
        super().save(*args, **kwargs)

    # ── Computed badges property (used by serializer) ────────────
    @property
    def badges(self) -> list[str]:
        """
        Returns a list of badge keys based on explicit flag fields.
        Displayed on business cards and detail pages.
        Order matters — featured first.
        """
        result = []
        if self.is_featured:
            result.append('featured')
        if self.is_verified:
            result.append('verified')
        if self.is_community_trusted:
            result.append('community')
        if self.is_responsive:
            result.append('fast')
        return result

    @property
    def badge_count(self) -> int:
        return len(self.badges)

    @property
    def is_fully_trusted(self) -> bool:
        """True if the business has at least verified + community badges."""
        return self.is_verified and self.is_community_trusted
