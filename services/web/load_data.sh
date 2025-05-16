#!/bin/sh
cd "$(dirname "$0")"
python3 ./generate_data.py \
  --db=postgresql://hello_flask:hello_flask@db:5432/hello_flask_dev \
  --users=1000 \
  --messages=100000 \
  --urls=0.1
