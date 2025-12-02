FROM python:3.11 AS builder

COPY requirements.txt .

RUN pip install -r requirements.txt

FROM python:3.11-slim 

WORKDIR /app


COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY src /app/src

#CMD ["uvicorn","src.main:app","--host","0.0.0.0","--port","8000"]