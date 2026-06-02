export interface Business {
  id: number
  name: string
  slug: string
  category: string
  category_slug: string
  description: string | null
  phone: string | null
  website: string | null
  address: string | null
  city: string
  state: string
  // Explicit trust flags
  is_verified: boolean
  is_featured: boolean
  is_responsive: boolean
  is_community_trusted: boolean
  // Computed
  reliability_score: number
  avg_response_time: string
  mention_count: number
  jobs_completed: number
  badges: BadgeKey[]
  created_at: string
}

export type BadgeKey = 'featured' | 'verified' | 'community' | 'fast'

export interface Review {
  id: number
  author_name: string
  text: string
  sentiment: 'positive' | 'neutral' | 'negative'
  source: string
  created_at_display: string
}

export type ArticleType = 'service_provider' | 'demand_report' | 'community' | 'warning' | 'local_news'

export interface NewsPost {
  id: number
  title: string
  slug: string
  excerpt: string
  content_html: string
  category: string
  article_type: ArticleType
  service_category_slug: string
  is_service_article: boolean
  shows_request_ui: boolean
  tags: string[]
  published_at: string
  read_time_minutes: number
  demand_snapshot: { service: string; count: number }[] | null
}

export interface Stats {
  verified_providers: number
  signals_this_month: number
  resolution_rate: number
  open_requests: number
}

export interface VendorProfile {
  id: number
  email: string
  full_name: string
  phone: string
  plan: 'free' | 'starter' | 'pro' | 'featured'
  onboarding_done: boolean
}

export interface VendorBusiness extends Business {
  is_pending_review: boolean
  rejection_reason: string
  callanchor_enabled: boolean
  callanchor_phone: string
  updated_at: string
}
