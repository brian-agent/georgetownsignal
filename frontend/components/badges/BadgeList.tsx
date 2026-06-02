import { ShieldCheck, Users, Clock, Star } from 'lucide-react'
import type { BadgeKey } from '@/types'

const BADGES: Record<BadgeKey, { label: string; cls: string; icon: React.ReactNode }> = {
  featured:  { label: 'Featured',           cls: 'gs-badge gs-badge-featured',  icon: <Star className="w-3 h-3" /> },
  verified:  { label: 'Signal Verified',     cls: 'gs-badge gs-badge-verified',  icon: <ShieldCheck className="w-3 h-3" /> },
  community: { label: 'Community Trusted',   cls: 'gs-badge gs-badge-community', icon: <Users className="w-3 h-3" /> },
  fast:      { label: 'Fastest Responder',   cls: 'gs-badge gs-badge-fast',      icon: <Clock className="w-3 h-3" /> },
}

export function BadgeList({ badges }: { badges: BadgeKey[] }) {
  return (
    <div className="flex flex-wrap gap-1.5">
      {badges.map(b => {
        const cfg = BADGES[b]
        if (!cfg) return null
        return (
          <span key={b} className={cfg.cls}>
            {cfg.icon} {cfg.label}
          </span>
        )
      })}
    </div>
  )
}
