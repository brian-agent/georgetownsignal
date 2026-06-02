# Georgetown Signal — LLM Sales Conversation Context

Use this document as context when having a sales conversation with a potential partner,
investor, vendor, or advertiser. Paste the relevant section into your LLM prompt.

---

## WHAT WE ARE

Georgetown Signal is a **local trust intelligence platform** built for Georgetown, Texas.
We are not a directory website. We are not a review app. We are not a local blog.

We are the **community's memory** — a system that converts real neighborhood conversations
into a ranked, verified, ranked index of local service providers, then routes demand
directly to those providers.

The simplest way to explain it:

> Google tells you who exists.
> Georgetown Signal tells you who your neighbors actually trust — and why.

---

## THE CORE INSIGHT

Every day, Georgetown residents post in Facebook groups:
*"Anyone know a good electrician?"*
*"Who should I avoid for roofing?"*
*"Bright Electric just saved us — highly recommend."*

Those posts are pre-search intent signals. They happen **before** anyone opens Google.
Yelp never sees them. Google never sees them. We capture them, structure them, and
turn them into a real-time trust index for every service category in Georgetown.

The result: when a resident searches "best electrician Georgetown TX," they land on
our article — not Yelp — because our content is built from actual community intelligence,
not ad spend.

---

## THE PRODUCT (what exists today)

**Public platform** (georgetownsignal.com):
- SEO-optimized directory with category pages (`/electricians-georgetown`,  `/plumbers-georgetown`)
- Business profiles with: reliability score (0–100), avg response time, community mention count
- Computed badge system: Signal Verified · Community Trusted · Fastest Responder · Featured
- Local news hub with 5 article types — service articles embed provider cards + request forms
- Service request flow: residents submit job requests → matched to verified providers
- Weekly newsletter: "Georgetown Signal Weekly" — top providers, demand data, community signals
- Live signal ticker showing real-time community activity

**Vendor portal** (vendor sign-up flow):
- Supabase Auth-powered signup/login — no custom auth
- 4-step onboarding: profile → business details → contact + CallAnchor → review
- Vendor dashboard: see live badge status, reliability score, mention count, lead activity
- Admin approval gate: all new listings are reviewed before going public

**Backend intelligence** (Django + Celery):
- Signal engine captures community conversations and extracts service signals
- Auto-computes Community Trusted badge when mention_count hits 10+
- Auto-computes Fastest Responder badge from CallAnchor response data (<45 min)
- Signal Verified and Featured badges are admin-only (manual vetting / paid)
- Weekly newsletter auto-generated from live platform data via Resend

**Tech stack**: Next.js 14 · Django 5 · Supabase (Postgres + Auth) · Redis + Celery · Vercel + Render

---

## THE BADGE SYSTEM (how trust is structured)

| Badge | How earned | Who sets it |
|-------|------------|-------------|
| ⭐ Featured | Paid upgrade | Admin only |
| 🛡 Signal Verified | Manual admin vetting | Admin only |
| 👥 Community Trusted | 10+ community mentions (auto) | Celery task |
| ⚡ Fastest Responder | Avg response < 45 min via CallAnchor (auto) | Celery task |

Vendors see exactly what they need to do to earn each badge. This creates
a natural upgrade path: free listing → get mentions → Community Trusted → get verified → Signal Verified → get featured → Featured.

---

## REVENUE MODEL

1. **Featured Listings** — paid monthly placement. Highest position in all category pages and homepage.
2. **Signal Verified Badge** — subscription access to the verification program. Requires CallAnchor enrollment.
3. **Lead Routing** — high-intent service requests routed to verified providers. Priced per lead or monthly.
4. **Sponsored Newsletter Spots** — fixed-fee placement in the weekly Georgetown Signal newsletter.
5. **Reputation Management** — managed review/mention monitoring for established businesses.

We deliberately avoid dependency on any single revenue stream.
The directory builds the audience. The newsletter builds retention. The badge system drives upgrades.

---

## WHY INCUMBENTS CAN'T COPY THIS

**Yelp**: Monetized through ads and promoted listings. Their incentive is to show businesses that pay — not businesses that communities trust. Their data is lagging (reviews happen after a job, not during community discussion). They cannot deploy a Georgetown-specific human intelligence layer without rebuilding their entire business model.

**Google Maps**: Algorithmic. Business-controlled listings. Zero behavioral signal from community discussions. No editorial voice. No local newsletter. No trust verification.

**Nextdoor**: Closest competitor, but structurally reactive — residents ask and forget. Nextdoor has no structured directory, no reliability scoring, no editorial layer, no lead routing, and no vendor portal. They also have weak penetration in the fast-growing Georgetown exurb market.

**Our moat**: We own the period *between* when someone decides they need a service and when they search Google. That's a structural advantage that ad spend cannot buy.

---

## GO-TO-MARKET: HOW WE'RE PUSHING THIS

### Phase 1 — Trust density in Georgetown (Months 1–3)

**Content before directory:**
We launch the news hub first, not the directory. The first 30 days are 3 articles/week:
- Service comparisons: "Which electricians actually show up in Georgetown?"
- New resident guides: "Just moved to Georgetown? Here's your first-year service list."
- Consumer warnings: "Georgetown contractor red flags — what residents flagged this month."
- Demand reports: "Georgetown's most requested services this week" (proprietary data, uncopiable).

Every article is SEO-targeted to a Georgetown + service keyword. We will outrank Yelp
on long-tail local queries within 60 days because our content has actual community data
behind it.

**Community presence:**
We join every major Georgetown Facebook group personally. We introduce ourselves as Georgetown Signal. We share our articles with group admins. We ask admins to pin our request form when residents ask for service recommendations. One admin sharing our content is worth 10,000 ad impressions.

**Manual seeding:**
The first 10 businesses in the directory are personally contacted by us. We explain the platform, the badge system, and the verification pathway. We onboard them for free. We ask for nothing except permission to track their response rate via CallAnchor. This is how we get the data that makes the platform valuable.

### Phase 2 — Vendor momentum (Months 3–6)

Once the directory has 20+ active listings and the newsletter has 500+ subscribers:
- We show vendors their mention count from community groups (their own data, collected by us)
- We offer Signal Verified at a monthly fee — it unlocks lead routing
- We run a "Georgetown's Most Trusted" campaign (top 5 providers in each category) — vendors compete to be on it
- We sell featured placement to the top 1–2 providers per category who want guaranteed visibility

The newsletter becomes a weekly appointment. Vendors pay for sponsorship because it reaches the exact audience of Georgetown homeowners making service decisions.

### Phase 3 — City replication (Month 6+)

The same codebase, deployed at `conroesignal.com`, `katysignal.com`, `sunsetvalleysignal.com`.
Same Django API. Same Supabase database. Different city/state env vars.
Content strategy is identical but seeded with local data.

Each new city launches faster because:
- The platform is proven
- Vendor onboarding is automated
- The SEO playbook is documented
- Adjacent vendors already know the Georgetown Signal brand

---

## KEY NUMBERS TO MENTION IN SALES CONVERSATIONS

- Georgetown grew 10.6% in a single year (2022–2023) — one of the fastest in the US
- 3,200 new homes completed in Georgetown in 2024 alone
- Every new homeowner needs: electrician, plumber, HVAC, roofer, landscaper — within year one
- Home services demand in Georgetown metro is up 22%+ YoY
- Platform runs at ~$24/month (Vercel + Render + Supabase free tier)
- Each vendor listing generates: 1 lead at $30 = platform cost covered

---

## TALKING TO A LOCAL SERVICE PROVIDER

**Opening:**
"You know those Facebook posts where someone asks 'who's the best electrician in Georgetown?' and 20 people respond? We track every single one of those. Right now your name has come up [X] times. I'd like to show you."

**The offer:**
"We're building the directory Georgetown residents check *before* they Google. We want you in it — for free, to start. All we ask is that you let us track your response rate so we can show residents you're reliable. Once you hit 10 community mentions, you automatically earn the Community Trusted badge. Once your response time drops below 45 minutes, you earn Fastest Responder. Then we talk about Signal Verified, which puts you at the top."

**The close:**
"You're not buying an ad. You're buying verified trust in a city where 3,000 new homeowners moved in last year who have no idea who to call. We want you to be the name they find."

---

## TALKING TO AN INVESTOR

"We're building a local trust index, starting with one of the fastest-growing cities in America. The business model is a trust certification ladder — free listing, earned badges, paid verification, featured placement. The go-to-market is content-first: we publish the articles that rank before anyone searches. The moat is community data that incumbents can't replicate without breaking their own business models. We're operational at $24/month and expanding city-by-city using the same codebase."

---

## TALKING TO A FACEBOOK GROUP ADMIN

"I run Georgetown Signal — a local platform that tracks what Georgetown residents recommend in community groups and turns it into a public directory. I'd love to partner with you. When someone asks for an electrician recommendation in your group, instead of 30 people posting different names, you could link to our verified list — ranked by actual response time and community mentions. It saves your members time and it saves you from moderating the same question every week."

---

*Georgetown Signal v2 · LocaleTrust Inc. · Georgetown, TX*
*Use this document as LLM context. Do not distribute externally.*
