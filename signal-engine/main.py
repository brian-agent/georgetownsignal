import os, requests, logging
from dotenv import load_dotenv
from processors.entity_extractor import parse_post

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_URL   = os.getenv('DJANGO_API_URL','http://localhost:8000')
API_TOKEN = os.getenv('DJANGO_API_TOKEN','')
HEADERS   = {'Authorization': f'Token {API_TOKEN}', 'Content-Type': 'application/json'}
FACEBOOK_GROUPS = []  # Add Georgetown TX group URLs here

def post_signal(signal):
    try:
        r = requests.post(f'{API_URL}/api/signals/', json=signal, headers=HEADERS, timeout=10)
        return r.status_code in (200, 201)
    except Exception as e:
        logger.error(f'Signal post failed: {e}'); return False

def run():
    if not FACEBOOK_GROUPS:
        logger.warning('No Facebook groups configured'); return
    from scrapers.facebook import run_scraper
    raw = run_scraper(FACEBOOK_GROUPS, os.getenv('FB_EMAIL'), os.getenv('FB_PASSWORD'))
    posted = sum(1 for r in raw if post_signal(parse_post(r)) if parse_post(r))
    logger.info(f'Posted {posted} signals')

if __name__ == '__main__': run()
