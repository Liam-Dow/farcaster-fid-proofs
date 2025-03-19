# Retrieve & Store Farcaster FID Proofs

A multithreaded Python script designed to efficiently scrape and store Farcaster user proofs in a SQLite database. 

## Overview

This tool connects to a [Hubble](https://www.thehubble.xyz/intro/hubble.html) host and systematically retrieves Farcaster user information (FID, username, and owner address) for a specified range of Farcaster IDs. It employs multithreading to optimize performance and includes features like connection pooling, retry logic, and progress tracking.

## Features

- **Multithreaded Processing**: Uses Python's ThreadPoolExecutor for concurrent API requests
- **Connection Pooling**: Maintains a pool of reusable HTTP sessions for improved performance
- **Error Handling**: Implements retry logic and comprehensive error logging
- **Progress Tracking**: Real-time logging of processing speed and completion status
- **Database Storage**: Efficiently stores retrieved data in a SQLite database

## Requirements

- Python 3.7+
- `requests` library
- SQLite3 (included in Python standard library)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/Liam-Dow/farcaster-fid-proofs
   cd farcaster-fid-proofs
   ```

2. Install dependencies:
   ```bash
   pip install requests
   ```

3. Configure the script settings in the CONFIG section (see Configuration below)

## Configuration

| Variable | Description | Default | 
|----------|-------------|---------|
| `DB_PATH` | Path to SQLite database file | '/path/to/your/sqlite/db.sqlite' |
| `FC_HOST` | Hubble hostname (Farcasters public Hubble host set as default) | 'nemes.farcaster.xyz' |
| `FC_HTTP_PORT` | HTTP port | 2281 |
| `START_FID` | First Farcaster ID to scrape | 1 |
| `END_FID` | Last Farcaster ID to scrape | 906000 |
| `MAX_WORKERS` | Maximum number of concurrent threads | 20 |
| `SESSION_POOL_SIZE` | Size of HTTP session pool | 10 |
| `REQUEST_TIMEOUT` | HTTP request timeout in seconds | 2 |
| `MAX_RETRIES` | Maximum number of retry attempts | 3 |
| `LOG_PROGRESS_INTERVAL` | How often to log progress (# of records) | 100 |

## Usage

Run the script with:

```bash
python farcaster_scraper.py
```

## Data Storage

Data is stored in a SQLite database with the following schema:

```sql
CREATE TABLE IF NOT EXISTS FARCASTER_ADDRESSES (
    fid INTEGER PRIMARY KEY,
    name TEXT,
    owner TEXT
)
```

Where:
- `fid`: Farcaster ID (primary key)
- `name`: Farcaster username 
- `owner`: Ethereum address of the account owner

## Performance Notes

- Adjust `MAX_WORKERS` based on your system capabilities and network conditions
- The script reports processing speed to help optimize settings
- Increasing `SESSION_POOL_SIZE` may improve throughput but increases memory usage


## Disclaimer

This tool is for educational and research purposes only. Please use responsibly and respect Farcaster's terms of service and rate limits.
