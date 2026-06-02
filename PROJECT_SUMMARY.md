# Georgetown Signal — Complete Project Summary

> **One-line pitch:** Georgetown Signal is a local trust intelligence platform that converts community conversations into a verified directory, news hub, and lead engine for home service providers in Georgetown, Texas.

---

## What It Is (and What It Is Not)

| It IS | It IS NOT |
|-------|-----------|
| A local trust index ranked by real community data | A standard business directory |
| A content-first SEO platform with 5 article types | A review site like Yelp |
| A vendor portal with badge-based upgrade paths | A SaaS product |
| A demand intelligence engine capturing pre-search intent | A paid ads marketplace |
| A local media brand (newsletter + news hub) | A social network |

---

## The Core Insight

Every day Georgetown residents post in Facebook groups:
*"Anyone know a good electrician?"*
*"Avoid Peak Electrical — they ghosted me."*
*"Bright Electric just saved us at 10pm — highly recommend."*

These posts are **pre-search intent signals**. They happen before anyone opens Google. Yelp never sees them. Google never sees them. Georgetown Signal captures them, structures them, and turns them into a real-time trust index for every service category in the city.

---

## Full Tech Stack

| Layer | Technology | Hosted On |
|-------|-----------|-----------|
| Frontend | Next.js 14 App Router + TypeScript | Vercel |
| Backend API | Django 5 + Django REST Framework | Render |
| Database | PostgreSQL via Supabase | Supabase |
| Authentication | Supabase Auth (JWT) | Supabase |
| Task Queue | Celery + Redis | Render |
| Email | Resend | External |
| Response Tracking | CallAnchor API | External |
| Signal Engine | Python + Selenium + NLP | VM / Cron |
| Styling | Tailwind CSS | — |

**Monthly cost to run:** ~$24/mo (Render $7 web + $7 worker + $10 Redis · Supabase free · Vercel free)

---

## Project Structure

```
georgetown-signal-v2/
├── README.md                    Deployment guide
├── SALES_CONTEXT.md             LLM sales conversation prompt
│
├── backend/                     Django REST API (Render)
│   ├── supabase_schema.sql      Full DB schema + RLS + seed data
│   ├── requirements.txt
│   ├── .env.example
│   ├── config/
│   │   ├── settings.py          Django config + Supabase JWT setup
│   │   ├── urls.py              Root URL router
│   │   ├── celery.py            Celery app + scheduled tasks
│   │   └── wsgi.py
│   ├── api/
│   │   ├── authentication.py    Supabase JWT → request.user
│   │   └── urls.py              All API endpoints
│   └── apps/
│       ├── businesses/          Core listing model + badge logic
│       ├── vendors/             Vendor profiles + protected views
│       ├── signals/             Community signal model + ticker
│       ├── reviews/             Community reviews
│       ├── leads/               Service requests + email routing
│       ├── newsletter/          Subscribers + weekly Celery send
│       ├── news/                Articles with article_type flag
│       └── stats/               Platform stats endpoint
│
├── frontend/                    Next.js 14 (Vercel)
│   ├── app/
│   │   ├── page.tsx             Homepage
│   │   ├── layout.tsx           Root layout (Navbar, Ticker, Footer)
│   │   ├── globals.css          Tailwind + brand design tokens
│   │   ├── business/[slug]/     Business detail page
│   │   ├── category/[slug]/     SEO category pages
│   │   ├── news/[slug]/         Article page with conversion panels
│   │   ├── request/             Service request form
│   │   ├── auth/
│   │   │   ├── signup/          Vendor signup (Supabase)
│   │   │   ├── login/           Vendor login (Supabase)
│   │   │   └── callback/        Supabase email confirmation handler
│   │   └── vendor/
│   │       ├── onboarding/      4-step listing creation wizard
│   │       └── dashboard/       Vendor dashboard + badge status
│   ├── components/
│   │   ├── layout/              Navbar, Footer, SignalTicker
│   │   ├── directory/           BusinessCard, HeroSection, CategoryGrid,
│   │   │                        StatsRow, TopProviders, RequestPanel, ReviewList
│   │   ├── news/                NewsPreview, ArticleConversionPanel
│   │   ├── badges/              BadgeList (computed from flags)
│   │   └── ui/                  NewsletterSignup, RequestButton
│   ├── hooks/
│   │   └── useVendorAuth.ts     Supabase session + authFetch wrapper
│   ├── lib/
│   │   ├── api.ts               Public API client
│   │   └── supabase.ts          Supabase browser client
│   └── types/index.ts           Full TypeScript types
│
└── signal-engine/               Python scraper (VM/cron)
    ├── main.py                  Pipeline runner
    ├── scrapers/facebook.py     Selenium FB group scraper
    ├── processors/
    │   └── entity_extractor.py  NLP: service detection, sentiment, entity extraction
    └── requirements.txt
```

---

## Database Schema (Supabase)

### Tables

| Table | Purpose | Key Fields |
|-------|---------|-----------|
| `auth.users` | Supabase-managed vendor accounts | id (UUID), email |
| `vendor_profiles` | Vendor metadata linked to auth | supabase_uid, plan, onboarding_done |
| `businesses` | All service provider listings | trust flags, metrics, supabase_uid |
| `signals` | Raw community intelligence | business_id, sentiment, raw_text |
| `reviews` | Community reviews per business | business_id, sentiment, source |
| `leads` | Resident service requests | category, urgency, status, contact |
| `newsletter_subscribers` | Email list | email, city, state |
| `news_posts` | Articles with article_type | slug, article_type, service_category_slug |

### Row Level Security

| Table | Public can | Vendor can | Admin (service role) |
|-------|-----------|-----------|----------------------|
| businesses | SELECT (active + approved) | INSERT/UPDATE own rows | All |
| vendor_profiles | — | SELECT/UPDATE own row | All |
| leads | INSERT | — | All |
| news_posts | SELECT (published) | — | All |
| reviews, signals | SELECT | — | All |
| newsletter_subscribers | INSERT | — | All |

---

## Business Model (Businesses) — The Heart of the Platform

### Trust Flags — 4 explicit booleans on every listing

```python
is_verified         = BooleanField  # Admin-only. Signal Verified badge.
is_featured         = BooleanField  # Admin-only. Paid. Featured badge.
is_responsive       = BooleanField  # Auto: avg_response_minutes < 45
is_community_trusted = BooleanField # Auto: mention_count >= 10
```

### Computed `badges` property

```python
@property
def badges(self) -> list[str]:
    result = []
    if self.is_featured:          result.append('featured')
    if self.is_verified:          result.append('verified')
    if self.is_community_trusted: result.append('community')
    if self.is_responsive:        result.append('fast')
    return result
```

### Badge reference

| Badge | Key | Set by | Unlock condition |
|-------|-----|--------|-----------------|
| ⭐ Featured | `featured` | Admin only | Paid upgrade |
| 🛡 Signal Verified | `verified` | Admin only | Manual vetting |
| 👥 Community Trusted | `community` | Celery auto | mention_count ≥ 10 |
| ⚡ Fastest Responder | `fast` | Celery auto | avg_response_minutes < 45 |

### Listing lifecycle

```
Vendor signs up (Supabase Auth)
        ↓
Completes 4-step onboarding wizard
        ↓
Listing created: is_pending_review=True
        ↓
Admin reviews in Django Admin
        ↓
Approved: is_pending_review=False → listing goes public
        ↓
Community mentions accumulate → is_community_trusted=True (auto)
        ↓
CallAnchor enrolled → is_responsive=True (auto)
        ↓
Admin grants is_verified=True → Signal Verified badge
        ↓
Vendor upgrades → is_featured=True → top placement + Featured badge
```

---

## Authentication Architecture

```
Vendor signs up / logs in → Supabase Auth
        ↓
Supabase issues JWT (HS256, signed with SUPABASE_JWT_SECRET)
        ↓
Frontend stores JWT in Supabase session
        ↓
authFetch() injects: Authorization: Bearer <jwt>
        ↓
Django: SupabaseJWTAuthentication validates JWT
        ↓
request.user = SupabaseUser(uid, email, role)
        ↓
Vendor views filter by request.user.supabase_uid
```

**No Django users. No sessions. No passwords stored in Django. Supabase owns identity entirely.**

---

## API Endpoints

### Public (no auth)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/businesses/` | Directory. Filter: `?category_slug=electricians&is_verified=true` |
| GET | `/api/businesses/{slug}/` | Business detail |
| GET | `/api/businesses/{slug}/reviews/` | Community reviews |
| GET | `/api/signals/ticker/` | Live ticker strings for UI |
| GET | `/api/news/` | Published posts. Filter: `?limit=3` |
| GET | `/api/news/{slug}/` | Full article |
| GET | `/api/stats/` | Platform stats |
| POST | `/api/leads/` | Submit service request |
| POST | `/api/newsletter/subscribe/` | Subscribe to newsletter |

### Vendor (Bearer JWT required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/vendor/profile/` | Read own profile |
| PATCH | `/api/vendor/profile/` | Update name, phone |
| GET | `/api/vendor/businesses/` | Own listings |
| POST | `/api/vendor/businesses/` | Create new listing |
| GET/PATCH | `/api/vendor/businesses/{id}/` | Read / update own listing |
| POST | `/api/vendor/onboarding/` | Mark onboarding complete |

---

## News Hub — Article Type System

Every article has an `article_type` field that controls what conversion UI renders.

| article_type | What renders | Use for |
|-------------|-------------|---------|
| `service_provider` | Inline provider cards + request form | Comparisons, "best X in Georgetown" |
| `demand_report` | Category-level request CTA + demand table | Weekly data reports |
| `warning` | "Find a verified provider" link to category | Contractor red flags |
| `community` | Newsletter signup only | Events, general news |
| `local_news` | Nothing — pure editorial | Schools, roads, development |

Articles also have `service_category_slug` (e.g. `electricians`) which auto-loads the top 4 verified providers from that category to embed inside `service_provider` articles.

---

## Celery Scheduled Tasks

| Task | Schedule | What it does |
|------|---------|-------------|
| `recalculate_reliability_scores` | Every 6 hours | Recalculates reliability_score from sentiment. Auto-sets is_responsive + is_community_trusted. **Never touches is_verified or is_featured.** |
| `aggregate_daily_signals` | Daily at midnight | Increments mention_count from new signals. Triggers is_community_trusted if ≥ 10. |
| `sync_callanchor_scores` | Every 6 hours | Pulls avg_response_minutes from CallAnchor API. Sets is_responsive. |
| `send_weekly_newsletter` | Fridays 8am CT | Builds and sends "Georgetown Signal Weekly" via Resend. |

---

## Signal Engine (Community Intelligence)

```
Facebook group posts
        ↓
Selenium scraper (facebook.py)
        ↓
entity_extractor.py:
  - detect_service()         → matches keywords to category
  - detect_sentiment()       → positive / negative / request / neutral
  - extract_business_names() → Title Case heuristic
  - extract_phone()          → regex
        ↓
Structured signal dict → POST /api/signals/
        ↓
Celery aggregation → mention_count++ → badge auto-update
```

**Important:** Facebook scraping violates Meta ToS. For production, use:
1. Facebook Groups API (requires Meta app approval)
2. Manual data entry via Django admin
3. Direct partnership with group admins

---

## Revenue Stack

| Stream | Mechanism | Who pays |
|--------|----------|---------|
| Featured Listings | Monthly fee, top placement, Featured badge | Established providers |
| Signal Verified | Subscription, unlocks lead routing | Growth-stage providers |
| Lead Routing | Per-lead or monthly fee | Verified providers |
| Newsletter Sponsorship | Fixed weekly slot | Any local business |
| Reputation Management | Managed service | High-value providers |

**The upgrade path is the product:**
Free listing → Community Trusted (earn it) → Signal Verified (pay for it) → Featured (pay more for it)

---

## Go-To-Market Plan

### Phase 1 — Content before directory (Months 1–3)

- Publish 3 articles/week targeting Georgetown + service keyword
- Types: service comparisons, new resident guides, consumer warnings, demand reports
- Join every Georgetown Facebook group personally
- Manually seed 10–15 businesses via Django admin (no vendor signups needed yet)
- Target: 500+ newsletter subscribers, 10+ businesses listed, ranking on 20+ keywords

### Phase 2 — Vendor momentum (Months 3–6)

- Open vendor self-signup
- Show vendors their mention count from community data (hooks them)
- Offer Signal Verified at $49/mo — includes CallAnchor + lead routing
- Run "Georgetown's Most Trusted" campaign — top 5 per category
- Target: 30+ active listings, 5+ paid vendors, $500/mo MRR

### Phase 3 — City replication (Month 6+)

- Clone to `conroesignal.com`, `katysignal.com` etc. (env var swap)
- Same Django API + Supabase DB (city field filters everything)
- Each city takes 6 weeks to SEO traction vs 12 weeks for Georgetown
- Target: 5 cities, 150+ listings, $3k/mo MRR

---

## SEO Strategy

- Category pages: `/electricians-georgetown`, `/plumbers-georgetown` — static ISR pages
- Question URLs: `/best-electricians-georgetown-tx`, `/who-to-call-plumber-georgetown`
- New resident guides: permanently rank because new people always move to Georgetown
- Demand reports: weekly freshness signal — Google prioritizes frequently updated local content
- Article type `service_provider` creates natural internal links: article → category page → business page

**Why we outrank Yelp:** Our content is written *from* community data about Georgetown specifically. Yelp's Georgetown pages are generated templates. Google rewards specificity.

---

## Deployment Checklist

### Supabase
- [ ] Create project
- [ ] Run `supabase_schema.sql` in SQL Editor
- [ ] Set Redirect URL to `https://georgetownsignal.com/auth/callback`
- [ ] Copy: DATABASE_URL, SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_KEY, SUPABASE_JWT_SECRET

### Render (backend)
- [ ] Connect GitHub repo → New Blueprint → `render.yaml`
- [ ] Set secret env vars: DATABASE_URL, SUPABASE_JWT_SECRET, RESEND_API_KEY, CALLANCHOR_API_KEY
- [ ] Shell: `python manage.py createsuperuser`
- [ ] Test: `https://georgetown-signal-api.onrender.com/api/stats/`

### Vercel (frontend)
- [ ] Import repo → Root Directory: `frontend`
- [ ] Set env vars: NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY, NEXT_PUBLIC_API_URL
- [ ] Add domain: `georgetownsignal.com`
- [ ] Test: visit homepage, try vendor signup

### Launch
- [ ] Seed 5 businesses via Django admin
- [ ] Publish first news article
- [ ] Send test newsletter via Resend
- [ ] Join Georgetown Facebook groups
- [ ] Submit sitemap to Google Search Console

---

## Key Numbers for Sales Conversations

- Georgetown pop. growth: **10.6% in one year** (2022–2023) — #2 fastest in US
- New homes completed 2024: **3,200**
- Home services demand growth: **22%+ YoY** in Georgetown metro
- Platform operating cost: **~$24/month**
- Break-even: **1 paid vendor at $24/mo** covers all infrastructure
- Badge upgrade path value: Free → $49/mo → $99/mo → $199/mo

---

## Critical Design Decisions & Why

| Decision | Why |
|----------|-----|
| Supabase Auth (not Django auth) | No password management, instant email confirmation, JWT auto-issued, RLS policies on DB level |
| Computed badges from explicit booleans | Booleans are fast to query, easy to filter in API, visible in admin, auditable. Logic lives in one `badges` property. |
| Admin-only is_verified + is_featured | Trust can't be self-assigned. Vendors earn community/fast automatically, buy verified/featured deliberately. |
| ISR (Incremental Static Regeneration) | Category and business pages are statically served (fast, cheap, SEO-perfect) but update every hour from live data |
| article_type flag on news posts | One field controls all conversion UI. No hardcoded logic per article. Adding a new type = one new branch. |
| CallAnchor on provider phone (not platform) | Platform never touches a call. Score is a measurement, not a service. Zero liability. |
| City-first, not broad coverage | Trust spreads socially, not geographically. One city dominated is worth more than 20 cities barely present. |
| Content before directory | Articles rank on Google before you have enough businesses to make the directory useful. Content builds the audience the directory monetizes. |

---

*Georgetown Signal v2 · LocaleTrust Inc. · Georgetown, TX*
*Last updated: May 2026*

---

## Review & Sentiment Pipeline (v2 addition)

### Three paths to get a review

| Path | Trigger | Source field | Verified |
|------|---------|-------------|---------|
| Direct review form | Resident visits `/business/{slug}` and clicks "Leave a review" | `direct` | No |
| Customer questionnaire | Sent by Celery when lead status → `matched` or `closed` | `questionnaire` | Yes (confirmed hire) |
| Community signal | Extracted from FB group post by signal engine | `signal` | No |

### Sentiment pipeline (Gemini 1.5 Flash)

```
Review submitted (any path)
        ↓
Saved with sentiment='pending'
        ↓
Celery: run_sentiment_analysis.delay(review.id)
        ↓
Gemini 1.5 Flash analyses text → returns JSON:
  { sentiment, score, reasoning, quote_excerpt, response_quality, would_recommend }
        ↓
Review updated: sentiment, sentiment_score, quote_excerpt
        ↓
recalculate_single_business.delay(business_id)
        ↓
reliability_score updated (60% signals + 40% direct reviews)
        ↓
Admin approves review → appears publicly
```

**Cost:** ~$0.000015 per review (Gemini 1.5 Flash). 1,000 reviews = $0.015.

### is_responsive badge — two paths

| Path | How | When |
|------|-----|------|
| CallAnchor (primary) | API polls CallAnchor for avg_response_minutes | Every 6 hours via Celery |
| Questionnaire (fallback) | Customer reports response time in feedback form | Aggregated hourly by Celery |

Both paths write to `avg_response_minutes`. Badge auto-sets when `avg_response_minutes < 45`.

### Article quotes

Every `service_provider` article can embed a community quote:
1. Admin flags a review as `is_featured_quote=True` in Django admin
2. Admin optionally writes a shorter `quote_excerpt`
3. OR Gemini auto-extracts `quote_excerpt` from the review text
4. `ArticleQuote` server component fetches best quote for the article's `service_category_slug`
5. Renders as a styled pull-quote inside the article body

**New API endpoints:**
- `POST /api/reviews/submit/` — direct customer review
- `GET /api/reviews/article-quote/?business_slug=X` — best quote for a business
- `GET/POST /api/reviews/questionnaire/{token}/` — token-based customer questionnaire

**New environment variable:**
- `GEMINI_API_KEY` — from [aistudio.google.com](https://aistudio.google.com) (free tier available)
- `FRONTEND_URL` — used for questionnaire links in emails
