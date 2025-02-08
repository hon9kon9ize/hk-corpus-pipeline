FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
ENV REPO_NAME=${REPO_NAME}
ENV HF_TOKEN=${HF_TOKEN}

COPY src .

CMD [ "scrape.py" ]