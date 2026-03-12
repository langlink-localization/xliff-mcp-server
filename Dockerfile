# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV HOST=0.0.0.0
ENV PORT=8000
ENV TZ=Asia/Shanghai

# Set working directory
WORKDIR /app

# Install system dependencies for lxml and translate-toolkit
RUN apt-get update && apt-get install -y \
    gcc \
    libxml2-dev \
    libxslt-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the application code
COPY README.md LICENSE pyproject.toml ./
COPY xliff_mcp/ ./xliff_mcp/

# Install the package
RUN python -m pip install --no-cache-dir .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port 8000
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from urllib.request import urlopen; urlopen('http://localhost:8000/health', timeout=5).read()" || exit 1

# Command to run the HTTP server
CMD ["python", "-m", "xliff_mcp.http_server"]
