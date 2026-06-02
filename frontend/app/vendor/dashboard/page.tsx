'use client'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { ShieldCheck, Star, Users, Clock, AlertCircle, CheckCircle, Edit } from 'lucide-react'
import { useVendorAuth } from '@/hooks/useVendorAuth'
import { BadgeList } from '@/components/badges/BadgeList'
import type { VendorBusiness, VendorProfile } from '@/types'

export default function VendorDashboard() {
  const router = useRouter()
  const { user, loading, signOut, authFetch } = useVendorAuth()
  const [profile,    setProfile]    = useState<VendorProfile | null>(null)
  const [businesses, setBusinesses] = useState<VendorBusiness[]>([])
  const [fetching,   setFetching]   = useState(true)

  useEffect(() => {
    if (!loading && !user) { router.push('/auth/login'); return }
    if (user) loadData()
  }, [user, loading])

  const loadData = async () => {
    try {
      const [pRes, bRes] = await Promise.all([
        authFetch('/api/vendor/profile/'),
        authFetch('/api/vendor/businesses/'),
      ])
      setProfile(await pRes.json())
      setBusinesses(await bRes.json())
    } finally { setFetching(false) }
  }

  if (loading || fetching) return (
    <div className="min-h-screen flex items-center justify-center">
      <p className="text-gray-400">Loading your dashboard…</p>
    </div>
  )

  const BADGE_EXPLAINERS = [
    { key: 'verified',  icon: <ShieldCheck className="w-5 h-5" />, label: 'Signal Verified',      how: 'Admin grants after vetting', admin: true },
    { key: 'featured',  icon: <Star className="w-5 h-5" />,        label: 'Featured',              how: 'Paid upgrade — contact us',  admin: true },
    { key: 'community', icon: <Users className="w-5 h-5" />,       label: 'Community Trusted',     how: 'Auto: 10+ community mentions', admin: false },
    { key: 'fast',      icon: <Clock className="w-5 h-5" />,       label: 'Fastest Responder',     how: 'Auto: avg response < 45 min via CallAnchor', admin: false },
  ]

  return (
    <div className="max-w-4xl mx-auto px-4 py-10">
      {/* Header */}
      <div className="flex items-start justify-between mb-8">
        <div>
          <h1 className="font-serif text-3xl text-brand-green">Vendor Dashboard</h1>
          <p className="text-gray-500 text-sm mt-1">{profile?.email}</p>
        </div>
        <div className="flex gap-3">
          <Link href="/auth/signup" className="gs-btn-outline text-xs py-2">Add listing</Link>
          <button onClick={signOut} className="text-sm text-gray-400 hover:text-gray-600">Sign out</button>
        </div>
      </div>

      {/* Listings */}
      <div className="space-y-6 mb-10">
        <h2 className="font-serif text-xl text-brand-ink">Your listings</h2>

        {businesses.length === 0 ? (
          <div className="gs-card text-center py-10">
            <p className="text-gray-400 text-sm mb-4">No listings yet.</p>
            <Link href="/vendor/onboarding" className="gs-btn-primary">Add your first listing</Link>
          </div>
        ) : businesses.map(biz => (
          <div key={biz.id} className="gs-card">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-xl bg-brand-green-light flex items-center justify-center flex-shrink-0">
                <span className="font-serif text-lg text-brand-green-mid">{biz.name.slice(0,2).toUpperCase()}</span>
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-3 mb-1">
                  <span className="font-medium text-brand-ink">{biz.name}</span>
                  {biz.is_pending_review ? (
                    <span className="inline-flex items-center gap-1 text-xs bg-amber-50 text-amber-700 px-2 py-0.5 rounded-full">
                      <AlertCircle className="w-3 h-3" /> Pending review
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 text-xs bg-brand-green-light text-brand-green px-2 py-0.5 rounded-full">
                      <CheckCircle className="w-3 h-3" /> Live
                    </span>
                  )}
                </div>
                <p className="text-xs text-gray-400 mb-2">{biz.category} · {biz.city}, {biz.state}</p>
                <BadgeList badges={biz.badges} />
              </div>
              <div className="text-right flex-shrink-0">
                <div className="font-serif text-2xl text-brand-green">{biz.reliability_score}%</div>
                <div className="text-xs text-gray-400">reliability</div>
                <Link href={`/vendor/edit?id=${biz.id}`}
                  className="inline-flex items-center gap-1 text-xs text-brand-green hover:underline mt-2">
                  <Edit className="w-3 h-3" /> Edit
                </Link>
              </div>
            </div>

            {/* Metrics row */}
            <div className="grid grid-cols-4 gap-3 mt-4 pt-4 border-t border-brand-rule">
              {[
                { label: 'Mentions', val: biz.mention_count },
                { label: 'Avg response', val: biz.avg_response_time },
                { label: 'Jobs done', val: biz.jobs_completed },
                { label: 'CallAnchor', val: biz.callanchor_enabled ? 'Active' : 'Off' },
              ].map(m => (
                <div key={m.label} className="text-center">
                  <div className="font-serif text-lg text-brand-green">{m.val}</div>
                  <div className="text-xs text-gray-400">{m.label}</div>
                </div>
              ))}
            </div>

            {/* Rejection reason */}
            {biz.rejection_reason && (
              <div className="mt-4 p-3 bg-red-50 border border-red-100 rounded-lg text-xs text-red-700">
                <strong>Rejection reason:</strong> {biz.rejection_reason}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Badge explainer */}
      <div className="gs-card">
        <h2 className="section-divider text-lg mb-4">How badges are earned</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {BADGE_EXPLAINERS.map(b => (
            <div key={b.key} className="flex gap-3 items-start">
              <div className="w-9 h-9 rounded-lg bg-brand-green-light flex items-center justify-center flex-shrink-0 text-brand-green">
                {b.icon}
              </div>
              <div>
                <div className="font-medium text-sm text-brand-ink">{b.label}</div>
                <div className="text-xs text-gray-500 mt-0.5">{b.how}</div>
                {b.admin && (
                  <span className="text-xs text-brand-amber">Admin-set</span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
