# Flutter web Dockerfile (template)
FROM cirrusci/flutter:stable-web

WORKDIR /app
COPY . .

RUN flutter build web

CMD ["flutter", "run", "-d", "web-server", "--web-port=8080", "--web-hostname=0.0.0.0"]
