import type { Business, NewsPost, Review, Stats } from '@/types'

const API = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

async function apiFetch<T>(path: string): Promise<T> {
  const res = await fetch(`${API}${path}`, { next: { revalidate: 3600 } })
  if (!res.ok) throw new Error(`API ${res.status}: ${path}`)
  return res.json()
}

export const getTopBusinesses = (limit = 5) =>
  apiFetch<Business[]>(`/api/businesses/?ordering=-is_featured,-reliability_score&limit=${limit}`)
    .catch(() => [] as Business[])

export const getBusiness = (slug: string) =>
  apiFetch<Business>(`/api/businesses/${slug}/`).catch(() => null)

export const getBusinessesByCategory = (slug: string) =>
  apiFetch<Business[]>(`/api/businesses/?category_slug=${slug}&ordering=-is_featured,-reliability_score`)
    .catch(() => [] as Business[])

export const getBusinessReviews = (slug: string) =>
  apiFetch<Review[]>(`/api/businesses/${slug}/reviews/`).catch(() => [] as Review[])

export const getLatestPosts = (limit = 6) =>
  apiFetch<NewsPost[]>(`/api/news/?ordering=-published_at&limit=${limit}`)
    .catch(() => [] as NewsPost[])

export const getPost = (slug: string) =>
  apiFetch<NewsPost>(`/api/news/${slug}/`).catch(() => null)

export const getStats = () =>
  apiFetch<Stats>('/api/stats/').catch(() =>
    ({ verified_providers: 0, signals_this_month: 0, resolution_rate: 0, open_requests: 0 }))

export const CATEGORIES = [
  { slug: 'electricians', label: 'Electricians' },
  { slug: 'plumbers',     label: 'Plumbers' },
  { slug: 'roofers',      label: 'Roofers' },
  { slug: 'hvac',         label: 'HVAC' },
  { slug: 'cleaners',     label: 'Cleaners' },
  { slug: 'movers',       label: 'Movers' },
  { slug: 'painters',     label: 'Painters' },
  { slug: 'landscapers',  label: 'Landscapers' },
]
