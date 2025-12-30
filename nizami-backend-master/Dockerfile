FROM python:3.9

WORKDIR /app

# Install system dependencies required for Aspose.Words (ICU libraries for .NET globalization)
# libicu-dev includes runtime libraries, but we also need to ensure ICU is available at runtime
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libicu-dev \
    libicu76 \
    && \
    ldconfig && \
    rm -rf /var/lib/apt/lists/*

# Set environment variable to ensure .NET can find ICU (Aspose.Words requirement)
ENV DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=false

# Copy requirements first for better caching
COPY requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . /app
#RUN python src/manage.py collectstatic --noinput

EXPOSE 8000

STOPSIGNAL SIGINT

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
