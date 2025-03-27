FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y chromium-driver chromium
ENV PATH="/usr/lib/chromium/:${PATH}"
CMD ["streamlit", "run", "app.py", "--server.port=8000", "--server.enableCORS=false"]
