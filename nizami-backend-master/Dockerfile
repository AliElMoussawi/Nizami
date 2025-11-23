FROM python:3.9

WORKDIR /app

# Install system dependencies required for Aspose.Words (ICU libraries for .NET globalization)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libicu-dev \
    icu-devtools && \
    rm -rf /var/lib/apt/lists/*

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
