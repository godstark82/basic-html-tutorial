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
RUN pip install instagrapi==2.1.5
RUN pip install torch==2.2.2
RUN pip install Pillow>=8.1.1
RUN pip install pydub==0.25.1
RUN pip install outetts==0.4.4
RUN pip install moviepy==1.0.3
RUN pip install google-ai-generativelanguage==0.6.15
RUN pip install google-api-core==2.24.2
RUN pip install google-api-python-client==2.170.0
RUN pip install google-auth==2.40.2
RUN pip install google-auth-httplib2==0.2.0
RUN pip install google-auth-oauthlib==1.2.2
RUN pip install google-genai==1.18.0
RUN pip install google-generativeai==0.8.5
RUN pip install googleapis-common-protos==1.70.0
RUN pip install gTTS==2.5.4

# Default env setup (use docker envs or .env file)
ENV IMAGEMAGICK_BINARY=/usr/bin/convert

# Run script
CMD ["python", "main.py"]
