FROM python:3.11-slim-bookworm

WORKDIR /srv

# Install base requirements first
RUN pip install streamlit --no-cache-dir

# Install OS dependencies
RUN apt-get update && apt-get install -y \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libpangoft2-1.0-0 \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy only the requirements and entrypoint first
COPY requirements.txt /srv/

COPY . /srv/

# Install Python dependencies
RUN pip install -r requirements.txt --no-cache-dir

# CMD to run the Streamlit app
CMD ["streamlit", "run", "/srv/app.py", \
    "--server.port=80", \
    "--server.headless=true", \
    "--server.address=0.0.0.0", \
    "--browser.gatherUsageStats=false", \
    "--server.enableStaticServing=true", \
    "--server.fileWatcherType=none", \
    "--client.toolbarMode=viewer"]
ENV PROJECT_ID=patient-unit-0339
