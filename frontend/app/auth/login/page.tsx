'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { createClient } from '@/lib/supabase'

export default function VendorLoginPage() {
  const router   = useRouter()
  const supabase = createClient()
  const [form, setForm]       = useState({ email: '', password: '' })
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true); setError('')
    const { error } = await supabase.auth.signInWithPassword(form)
    setLoading(false)
    if (error) setError(error.message)
    else router.push('/vendor/dashboard')
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-brand-parchment px-4">
      <div className="max-w-sm w-full">
        <div className="text-center mb-8">
          <Link href="/" className="font-serif text-2xl text-brand-green">
            Georgetown<span className="text-brand-amber">Signal</span>
          </Link>
          <h1 className="font-serif text-3xl text-brand-ink mt-4 mb-1">Vendor sign in</h1>
          <p className="text-gray-500 text-sm">Manage your Georgetown Signal listing</p>
        </div>

        <form onSubmit={handleSubmit} className="gs-card space-y-4">
          <div>
            <label className="gs-label">Email</label>
            <input required type="email" value={form.email}
              onChange={e => setForm({...form, email: e.target.value})}
              className="gs-input" />
          </div>
          <div>
            <label className="gs-label">Password</label>
            <input required type="password" value={form.password}
              onChange={e => setForm({...form, password: e.target.value})}
              className="gs-input" />
          </div>
          {error && <p className="text-red-500 text-sm">{error}</p>}
          <button type="submit" disabled={loading} className="gs-btn-primary w-full py-3 text-center">
            {loading ? 'Signing in…' : 'Sign in'}
          </button>
        </form>

        <p className="text-center text-sm text-gray-500 mt-4">
          No account?{' '}
          <Link href="/auth/signup" className="text-brand-green hover:underline">List your business free</Link>
        </p>
      </div>
    </div>
  )
}
