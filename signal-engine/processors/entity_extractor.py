import re
from typing import Optional

SERVICE_KEYWORDS = {
    'Electricians': ['electrician','electric','wiring','fuse','outlet','panel'],
    'Plumbers':     ['plumber','plumbing','pipe','drain','leak','water heater'],
    'Roofers':      ['roofer','roofing','roof','shingle','hail damage'],
    'HVAC':         ['hvac','ac','air conditioning','furnace','heat pump'],
    'Cleaners':     ['cleaner','cleaning','maid','housekeeping'],
    'Landscapers':  ['landscaper','landscaping','lawn','mowing','yard'],
    'Painters':     ['painter','painting','interior paint'],
    'Movers':       ['mover','moving','relocation'],
}
REQUEST_PHRASES  = ['anyone know','looking for','need a','need an','recommend','who do you use']
POSITIVE_PHRASES = ['highly recommend','great job','amazing','excellent','saved us','5 stars']
NEGATIVE_PHRASES = ['avoid','terrible','worst','scam','never again','overcharged']
PHONE_RE   = re.compile(r'(\(?\d{3}\)?[\s.\-]?\d{3}[\s.\-]?\d{4})')
BIZ_NAME_RE = re.compile(r'\b([A-Z][a-z]+(?:\s[A-Z][a-z]+){1,3})\b')
STOPWORDS   = {'Anyone','Does','Can','The','Georgetown','Texas','Looking'}

def detect_service(text):
    t = text.lower()
    for svc, kws in SERVICE_KEYWORDS.items():
        if any(k in t for k in kws): return svc
    return None

def detect_sentiment(text):
    t = text.lower()
    if any(p in t for p in NEGATIVE_PHRASES): return 'negative'
    if any(p in t for p in POSITIVE_PHRASES): return 'positive'
    if any(p in t for p in REQUEST_PHRASES):  return 'request'
    return 'neutral'

def parse_post(raw: dict) -> Optional[dict]:
    text = raw.get('raw_text','').strip()
    if not text or len(text) < 30: return None
    service = detect_service(text)
    if not service: return None
    names = [m for m in BIZ_NAME_RE.findall(text) if m not in STOPWORDS]
    phone = PHONE_RE.search(text)
    return {
        'business_name': names[0] if names else None,
        'service': service, 'mentions': 1,
        'source': raw.get('source',''), 'raw_text': text,
        'sentiment': detect_sentiment(text),
        'phone': phone.group(0) if phone else None,
        'timestamp': raw.get('timestamp'),
        'city': 'Georgetown', 'state': 'TX',
    }
