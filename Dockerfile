# Use Python 3.11
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=7860

# Install system dependencies for OpenCV, Cairo, and PostgreSQL
# Note: libgl1-mesa-glx is replaced by libgl1 in newer Debian versions
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libcairo2 \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user (Hugging Face preference)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

# Copy and install requirements
COPY --chown=user:user requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the rest of the application
COPY --chown=user:user . .

# Expose the HF default port
EXPOSE 7860

# Start the application on port 7860
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
