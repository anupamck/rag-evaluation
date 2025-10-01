# Lightweight Python base image
FROM python:3.13-slim

WORKDIR /workspace

# Install Python deps first (better layer caching)
COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip \
    && pip install -r /tmp/requirements.txt

CMD ["jupyter", "lab","--config=jupyter_server_config.py"]


