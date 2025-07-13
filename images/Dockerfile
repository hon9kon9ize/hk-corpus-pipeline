FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Hong Kong timezone
RUN apt-get update && apt-get install -y tzdata && \
  ln -sf /usr/share/zoneinfo/Asia/Hong_Kong /etc/localtime && \
  echo "Asia/Hong_Kong" > /etc/timezone && \
  apt-get clean && rm -rf /var/lib/apt/lists/*

COPY . .

ENTRYPOINT ["python"]