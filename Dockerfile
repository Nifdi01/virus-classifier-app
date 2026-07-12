FROM python:3.14-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
  build-essential \
  libgomp1 \
  curl \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip

# Install torch separately first — it's the largest download by far.
# Isolating it in its own layer means if a LATER package fails,
# Docker won't have to re-download torch again on retry.
RUN pip install --no-cache-dir \
  --index-url https://download.pytorch.org/whl/cpu \
  torch==2.12.0

# Now install everything else
RUN pip install --no-cache-dir \
  --default-timeout=180 \
  --retries=15 \
  -r requirements.txt
