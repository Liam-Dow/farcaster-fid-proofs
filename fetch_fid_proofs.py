import requests
import sqlite3
import logging
from threading import Lock
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# --------------------------------
# CONFIG
# --------------------------------

DB_PATH = '/path/to/your/sqlite/db.sqlite'
FC_HOST = "nemes.farcaster.xyz" 
FC_HTTP_PORT = 2281
START_FID = 1
END_FID = 906000
MAX_WORKERS = 20
SESSION_POOL_SIZE = 10
REQUEST_TIMEOUT = 2
MAX_RETRIES = 3 
LOG_PROGRESS_INTERVAL = 100

# --------------------------------
# END OF CONFIG
# --------------------------------

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class FarcasterScraper:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.host = FC_HOST
        self.http_port = FC_HTTP_PORT
        self.sessions = [requests.Session() for _ in range(SESSION_POOL_SIZE)]
        self.processed_count = 0
        self.lock = Lock()
        self._init_database()

    def _init_database(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS FARCASTER_ADDRESSES (
                    fid INTEGER PRIMARY KEY,
                    name TEXT,
                    owner TEXT
                )
            ''')

    def _fetch_user_proof(self, fid):
        """ Fetch user proof from Farcaster API and store in the database """
        session = self.sessions[fid % SESSION_POOL_SIZE] 

        for attempt in range(MAX_RETRIES):
            try:
                url = f'https://{self.host}:{self.http_port}/v1/userNameProofsByFid?fid={fid}'
                response = session.get(url, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                data = response.json()
                
                if data.get('proofs'): 
                    proof = data['proofs'][0]
                    self._save_to_database({
                        'fid': proof['fid'],
                        'name': proof['name'],
                        'owner': proof['owner']
                    })

                    with self.lock:
                        self.processed_count += 1
                return 

            except requests.RequestException as e:
                if attempt == MAX_RETRIES - 1:
                    logging.warning(f"Failed to fetch FID {fid} after {MAX_RETRIES} attempts: {e}")

    def _save_to_database(self, data):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    'INSERT OR REPLACE INTO FARCASTER_ADDRESSES (fid, name, owner) VALUES (?, ?, ?)',
                    (data['fid'], data['name'], data['owner'])
                )
        except sqlite3.Error as e:
            logging.error(f"Database error while saving FID {data['fid']}: {e}")

    def run(self, start_fid=START_FID, end_fid=END_FID, max_workers=MAX_WORKERS):
        """ Runs the scraper with multithreading """
        self.start_time = time.time()
        self.processed_count = 0

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(self._fetch_user_proof, fid): fid for fid in range(start_fid, end_fid + 1)}
            
            for future in as_completed(futures):
                fid = futures[future]
                try:
                    future.result()
                except Exception as e:
                    logging.error(f"Unexpected error processing FID {fid}: {e}")

                if self.processed_count % LOG_PROGRESS_INTERVAL == 0 and self.processed_count > 0:
                    elapsed = time.time() - self.start_time
                    rate = self.processed_count / elapsed
                    logging.info(f"Processed {self.processed_count} records. Rate: {rate:.2f} records/second")

if __name__ == "__main__":
    scraper = FarcasterScraper(db_path=DB_PATH)
    scraper.run()
