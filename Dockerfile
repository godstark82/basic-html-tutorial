FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    imagemagick \
    && rm -rf /var/lib/apt/lists/*

# Copy code and assets
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Default env setup (use docker envs or .env file)
ENV IMAGEMAGICK_BINARY=/usr/bin/convert
ARG GOOGLE_API_KEY
ARG GEMINI_MODEL
ARG YOUTUBE_TOKEN
ENV GOOGLE_API_KEY=$GOOGLE_API_KEY
ENV GEMINI_MODEL=$GEMINI_MODEL
ENV YOUTUBE_TOKEN=$YOUTUBE_TOKEN

# Run script
CMD ["python", "main.py"]
