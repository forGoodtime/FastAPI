FROM python:3.13.3

WORKDIR /app

RUN apt-get update && apt-get install -y python3-distutils

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]