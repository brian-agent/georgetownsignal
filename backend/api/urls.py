from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.businesses.views  import BusinessViewSet
from apps.signals.views     import SignalViewSet, ticker_view
from apps.reviews.views     import (
    ReviewViewSet, ReviewSubmitView,
    ArticleQuoteView, QuestionnaireView,
)
from apps.leads.views       import LeadCreateView
from apps.newsletter.views  import SubscribeView
from apps.news.views        import NewsPostViewSet
from apps.stats.views       import StatsView
from apps.vendors.views     import (
    VendorProfileView, VendorBusinessView,
    VendorBusinessListView, VendorOnboardingView,
)

router = DefaultRouter()
router.register(r'businesses', BusinessViewSet, basename='business')
router.register(r'signals',    SignalViewSet,   basename='signal')
router.register(r'reviews',    ReviewViewSet,   basename='review')
router.register(r'news',       NewsPostViewSet, basename='news')

urlpatterns = [
    # ── Public ──────────────────────────────────────────────────
    path('', include(router.urls)),
    path('leads/',                    LeadCreateView.as_view(),    name='lead-create'),
    path('newsletter/subscribe/',     SubscribeView.as_view(),     name='newsletter-subscribe'),
    path('signals/ticker/',           ticker_view,                 name='signal-ticker'),
    path('stats/',                    StatsView.as_view(),         name='stats'),

    # ── Reviews ──────────────────────────────────────────────────
    path('reviews/submit/',           ReviewSubmitView.as_view(),  name='review-submit'),
    path('reviews/article-quote/',    ArticleQuoteView.as_view(),  name='article-quote'),
    path('reviews/questionnaire/<str:token>/', QuestionnaireView.as_view(), name='questionnaire'),

    # ── Vendor (JWT required) ────────────────────────────────────
    path('vendor/profile/',               VendorProfileView.as_view(),      name='vendor-profile'),
    path('vendor/onboarding/',            VendorOnboardingView.as_view(),   name='vendor-onboarding'),
    path('vendor/businesses/',            VendorBusinessListView.as_view(), name='vendor-biz-list'),
    path('vendor/businesses/<int:pk>/',   VendorBusinessView.as_view(),     name='vendor-biz-detail'),
]
