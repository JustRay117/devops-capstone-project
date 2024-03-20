FROM python:3.9-slim

# Create Working Dir and install Dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Source Code of Application
COPY service/ ./service/

# Add User and Change Ownership of /app dir
RUN useradd --uid 1000 aelia && chown -R aelia /app

# Run service
EXPOSE 8080
CMD ["gunicorn", "--bind=0.0.0.0:8080", "--log-level=info", "service:app"]

# docker run --rm \
#   --link postgresql \
#   -p 8080:8080 \
#   -e DATABASE_URI=postgresql://postgres:postgres@postgresql:5432/postgres \
#   accounts