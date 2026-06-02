import { Quote } from 'lucide-react'

interface Props {
  businessSlug: string
  businessName: string
}

interface QuoteData {
  author_name: string
  quote_excerpt: string
  source: string
  created_at_display: string
}

async function fetchQuote(slug: string): Promise<QuoteData | null> {
  try {
    const res = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/api/reviews/article-quote/?business_slug=${slug}`,
      { next: { revalidate: 3600 } }
    )
    if (!res.ok) return null
    return res.json()
  } catch {
    return null
  }
}

/**
 * Server component — fetches the best featured quote for a business
 * and renders it as a pull-quote inside news articles.
 *
 * Usage in service_provider articles:
 *   <ArticleQuote businessSlug="bright-electric" businessName="Bright Electric" />
 *
 * Returns null silently if no approved quote exists yet.
 */
export async function ArticleQuote({ businessSlug, businessName }: Props) {
  const quote = await fetchQuote(businessSlug)
  if (!quote?.quote_excerpt) return null

  return (
    <figure className="my-8 border-l-4 border-brand-amber pl-5 py-1">
      <Quote className="w-5 h-5 text-brand-amber mb-2 opacity-60" />
      <blockquote className="font-serif text-lg text-brand-ink leading-relaxed italic">
        "{quote.quote_excerpt}"
      </blockquote>
      <figcaption className="mt-3 text-xs text-gray-400 not-italic">
        — {quote.author_name}
        {quote.source && quote.source !== 'direct' && (
          <span className="ml-1 text-gray-300">· {quote.source}</span>
        )}
        <span className="ml-1 text-gray-300">· {quote.created_at_display}</span>
      </figcaption>
    </figure>
  )
}
