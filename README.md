# Upwork Jobs Statistics Bot

## Machine Environ
Windows 10, Python 3.9.x

## Run
```bash
python -m venv .venv && source .venv/bin/activate
pip install -U pip
pip install -e .
bash scripts/run_dev.sh
```
## Run
```bash
python -m venv .venv
.venv\Scripts\activate
pip install fastapi uvicorn sqlalchemy pydantic-settings apscheduler

.env file
read_only_mode=false
enable_scheduler=true
poll_interval_seconds=120

start the system
uvicorn app.main:app --loop asyncio