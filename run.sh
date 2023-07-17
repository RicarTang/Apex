#!/bin/bash
python3 -m gunicorn main:app --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:4000
