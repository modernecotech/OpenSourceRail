FROM python:3.13.12-slim@sha256:f1927c75e81efd1e091dbd64b6c0ecaa5630b38635a3d1c04034ac636e1f94c8
WORKDIR /app
COPY services/integration/osr_integration /app/osr_integration
ENV PYTHONUNBUFFERED=1
CMD ["python", "-m", "osr_integration.server"]
