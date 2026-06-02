from django.contrib import admin
from django.utils.html import format_html
from .models import Business


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'category', 'city',
        'trust_badges_display',
        'reliability_score', 'mention_count', 'avg_response_time',
        'is_pending_review', 'is_active',
    )
    list_filter  = (
        'is_pending_review', 'is_active',
        'is_verified', 'is_featured', 'is_responsive', 'is_community_trusted',
        'category', 'city',
    )
    search_fields    = ('name', 'phone', 'address', 'supabase_uid')
    prepopulated_fields = {'slug': ('name',)}
    ordering         = ('-is_pending_review', '-created_at')
    readonly_fields  = ('supabase_uid', 'created_at', 'updated_at',
                        'reliability_score', 'mention_count',
                        'is_responsive', 'is_community_trusted')
    actions          = ['approve_listings', 'reject_listings',
                        'grant_verified', 'revoke_verified',
                        'grant_featured', 'revoke_featured']

    fieldsets = (
        ('Business Info', {
            'fields': ('name', 'slug', 'category', 'category_slug',
                       'description', 'phone', 'website', 'address', 'city', 'state')
        }),
        ('Admin Trust Flags', {
            'fields': ('is_verified', 'is_featured'),
            'description': 'These two flags are set manually by admins only.',
        }),
        ('Auto-Computed Flags (read-only)', {
            'fields': ('is_responsive', 'is_community_trusted',
                       'reliability_score', 'mention_count',
                       'avg_response_time', 'avg_response_minutes', 'jobs_completed'),
            'classes': ('collapse',),
        }),
        ('CallAnchor', {
            'fields': ('callanchor_enabled', 'callanchor_phone', 'callanchor_score'),
            'classes': ('collapse',),
        }),
        ('Status', {
            'fields': ('is_active', 'is_pending_review', 'rejection_reason'),
        }),
        ('Ownership', {
            'fields': ('supabase_uid', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def trust_badges_display(self, obj):
        badges = obj.badges
        html   = ''
        colors = {
            'featured':  ('#534AB7', '#EEEDFE'),
            'verified':  ('#0F6E56', '#E1F5EE'),
            'community': ('#185FA5', '#E6F1FB'),
            'fast':      ('#854F0B', '#FAEEDA'),
        }
        for b in badges:
            fg, bg = colors.get(b, ('#333', '#eee'))
            html += (f'<span style="background:{bg};color:{fg};padding:2px 7px;'
                     f'border-radius:10px;font-size:11px;margin-right:3px;">{b}</span>')
        return format_html(html) if html else '—'
    trust_badges_display.short_description = 'Badges'

    # ── Bulk actions ─────────────────────────────────────────────
    @admin.action(description='✅ Approve selected listings')
    def approve_listings(self, request, queryset):
        queryset.update(is_pending_review=False, is_active=True)

    @admin.action(description='❌ Reject selected listings')
    def reject_listings(self, request, queryset):
        queryset.update(is_active=False, is_pending_review=False,
                        rejection_reason='Rejected by admin.')

    @admin.action(description='🛡 Grant Signal Verified badge')
    def grant_verified(self, request, queryset):
        queryset.update(is_verified=True)

    @admin.action(description='Remove Signal Verified badge')
    def revoke_verified(self, request, queryset):
        queryset.update(is_verified=False)

    @admin.action(description='⭐ Grant Featured badge')
    def grant_featured(self, request, queryset):
        queryset.update(is_featured=True)

    @admin.action(description='Remove Featured badge')
    def revoke_featured(self, request, queryset):
        queryset.update(is_featured=False)
