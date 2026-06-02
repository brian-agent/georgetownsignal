'use client'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useVendorAuth } from '@/hooks/useVendorAuth'
import { CATEGORIES } from '@/lib/api'
import { ShieldCheck } from 'lucide-react'

const STEPS = ['Your profile', 'Business details', 'Contact info', 'Review & submit']

export default function VendorOnboardingPage() {
  const router = useRouter()
  const { user, loading, authFetch } = useVendorAuth()
  const [step, setStep] = useState(0)
  const [submitting, setSubmitting] = useState(false)
  const [done, setDone] = useState(false)

  const [profile, setProfile] = useState({ full_name: '', phone: '' })
  const [biz, setBiz]         = useState({
    name: '', category: '', category_slug: '',
    description: '', phone: '', website: '', address: '',
    city: 'Georgetown', state: 'TX',
    callanchor_enabled: false, callanchor_phone: '',
  })

  useEffect(() => {
    if (!loading && !user) router.push('/auth/login')
  }, [user, loading])

  const handleFinalSubmit = async () => {
    setSubmitting(true)
    try {
      // Save profile
      await authFetch('/api/vendor/profile/', {
        method: 'PATCH', body: JSON.stringify(profile),
      })
      // Create listing
      await authFetch('/api/vendor/businesses/', {
        method: 'POST', body: JSON.stringify(biz),
      })
      // Mark onboarding done
      await authFetch('/api/vendor/onboarding/', { method: 'POST' })
      setDone(true)
    } catch (e) {
      console.error(e)
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) return <div className="min-h-screen flex items-center justify-center"><p className="text-gray-400">Loading…</p></div>

  if (done) return (
    <div className="min-h-screen flex items-center justify-center bg-brand-parchment px-4">
      <div className="max-w-md text-center">
        <ShieldCheck className="w-14 h-14 text-brand-green mx-auto mb-4" />
        <h1 className="font-serif text-3xl text-brand-green mb-2">Listing submitted!</h1>
        <p className="text-gray-500 text-sm leading-relaxed mb-6">
          Your listing is under review. We'll approve it within 24 hours. Once live, you'll start appearing in Georgetown Signal search results and category pages.
        </p>
        <button onClick={() => router.push('/vendor/dashboard')} className="gs-btn-primary">
          Go to dashboard
        </button>
      </div>
    </div>
  )

  return (
    <div className="min-h-screen bg-brand-parchment py-12 px-4">
      <div className="max-w-lg mx-auto">
        {/* Progress */}
        <div className="mb-8">
          <div className="font-serif text-xl text-brand-green text-center mb-4">List your business</div>
          <div className="flex gap-2">
            {STEPS.map((s, i) => (
              <div key={s} className="flex-1">
                <div className={`h-1.5 rounded-full ${i <= step ? 'bg-brand-green' : 'bg-brand-rule'}`} />
                <div className={`text-xs mt-1 text-center truncate ${i === step ? 'text-brand-green font-medium' : 'text-gray-400'}`}>{s}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="gs-card">
          {/* Step 0: Profile */}
          {step === 0 && (
            <div className="space-y-4">
              <h2 className="font-serif text-xl text-brand-ink">Your profile</h2>
              <div>
                <label className="gs-label">Full name</label>
                <input type="text" value={profile.full_name}
                  onChange={e => setProfile({...profile, full_name: e.target.value})}
                  className="gs-input" placeholder="Your name" />
              </div>
              <div>
                <label className="gs-label">Phone</label>
                <input type="tel" value={profile.phone}
                  onChange={e => setProfile({...profile, phone: e.target.value})}
                  className="gs-input" placeholder="512-555-0100" />
              </div>
            </div>
          )}

          {/* Step 1: Business details */}
          {step === 1 && (
            <div className="space-y-4">
              <h2 className="font-serif text-xl text-brand-ink">Business details</h2>
              <div>
                <label className="gs-label">Business name *</label>
                <input required type="text" value={biz.name}
                  onChange={e => setBiz({...biz, name: e.target.value})}
                  className="gs-input" placeholder="Bright Electric LLC" />
              </div>
              <div>
                <label className="gs-label">Service category *</label>
                <select required value={biz.category_slug}
                  onChange={e => {
                    const cat = CATEGORIES.find(c => c.slug === e.target.value)
                    setBiz({...biz, category_slug: e.target.value, category: cat?.label ?? ''})
                  }}
                  className="gs-input">
                  <option value="">Select a category…</option>
                  {CATEGORIES.map(c => <option key={c.slug} value={c.slug}>{c.label}</option>)}
                </select>
              </div>
              <div>
                <label className="gs-label">Description</label>
                <textarea rows={3} value={biz.description}
                  onChange={e => setBiz({...biz, description: e.target.value})}
                  className="gs-input resize-none"
                  placeholder="Tell Georgetown residents what makes you the best choice…" />
              </div>
            </div>
          )}

          {/* Step 2: Contact */}
          {step === 2 && (
            <div className="space-y-4">
              <h2 className="font-serif text-xl text-brand-ink">Contact info</h2>
              <div>
                <label className="gs-label">Business phone *</label>
                <input required type="tel" value={biz.phone}
                  onChange={e => setBiz({...biz, phone: e.target.value})}
                  className="gs-input" placeholder="512-555-0100" />
              </div>
              <div>
                <label className="gs-label">Website</label>
                <input type="url" value={biz.website}
                  onChange={e => setBiz({...biz, website: e.target.value})}
                  className="gs-input" placeholder="https://yourbusiness.com" />
              </div>
              <div>
                <label className="gs-label">Service address</label>
                <input type="text" value={biz.address}
                  onChange={e => setBiz({...biz, address: e.target.value})}
                  className="gs-input" placeholder="Georgetown, TX 78626" />
              </div>
              <div className="border border-brand-rule rounded-lg p-4 bg-brand-green-light">
                <div className="flex items-start gap-3">
                  <input type="checkbox" id="ca" checked={biz.callanchor_enabled}
                    onChange={e => setBiz({...biz, callanchor_enabled: e.target.checked})}
                    className="mt-0.5" />
                  <label htmlFor="ca" className="text-sm text-brand-green cursor-pointer">
                    <span className="font-medium">Enable CallAnchor response tracking</span><br />
                    <span className="text-xs text-brand-green-mid">Unlock the Fastest Responder badge. We track your response rate and display it on your listing.</span>
                  </label>
                </div>
                {biz.callanchor_enabled && (
                  <input type="tel" value={biz.callanchor_phone}
                    onChange={e => setBiz({...biz, callanchor_phone: e.target.value})}
                    className="gs-input mt-3" placeholder="Phone number for CallAnchor tracking" />
                )}
              </div>
            </div>
          )}

          {/* Step 3: Review */}
          {step === 3 && (
            <div className="space-y-4">
              <h2 className="font-serif text-xl text-brand-ink">Review & submit</h2>
              <div className="space-y-2 text-sm text-gray-600">
                <div className="flex justify-between py-2 border-b border-brand-rule">
                  <span className="font-medium text-gray-500">Business</span>
                  <span>{biz.name || '—'}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-brand-rule">
                  <span className="font-medium text-gray-500">Category</span>
                  <span>{biz.category || '—'}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-brand-rule">
                  <span className="font-medium text-gray-500">Phone</span>
                  <span>{biz.phone || '—'}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-brand-rule">
                  <span className="font-medium text-gray-500">CallAnchor</span>
                  <span>{biz.callanchor_enabled ? '✓ Enabled' : 'Not enrolled'}</span>
                </div>
              </div>
              <div className="bg-brand-amber-light rounded-lg p-3 text-xs text-amber-800 leading-relaxed">
                Your listing will be reviewed within 24 hours. The <strong>Signal Verified</strong> badge is granted after admin vetting. The <strong>Fastest Responder</strong> badge is auto-computed from CallAnchor data. The <strong>Community Trusted</strong> badge unlocks when you reach 10+ community mentions.
              </div>
            </div>
          )}

          {/* Navigation */}
          <div className="flex gap-3 mt-6">
            {step > 0 && (
              <button onClick={() => setStep(step - 1)}
                className="gs-btn-outline flex-1">← Back</button>
            )}
            {step < 3 ? (
              <button onClick={() => setStep(step + 1)}
                className="gs-btn-primary flex-1">Continue →</button>
            ) : (
              <button onClick={handleFinalSubmit} disabled={submitting}
                className="gs-btn-primary flex-1">
                {submitting ? 'Submitting…' : 'Submit listing'}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
