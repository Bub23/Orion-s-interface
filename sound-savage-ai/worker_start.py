#!/usr/bin/env python
"""
Worker startup script
Run: celery -A app.workers.celery_app worker --loglevel=info
Or: python worker_start.py
"""

from app.workers.celery_app import celery_app

if __name__ == "__main__":
    celery_app.start([
        "worker",
        "--loglevel=info",
        "--queues=content_pipeline,render,analytics",
        "--concurrency=4"
    ])
