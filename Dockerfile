FROM eclipse-temurin:17-jdk-jammy AS verapdf-installer

ARG VERAPDF_VERSION=1.30
ARG VERAPDF_PATCH_VERSION=2
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl unzip \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /tmp
COPY docker-install.xml /tmp/docker-install.xml
RUN curl -fsSL \
      "https://software.verapdf.org/rel/${VERAPDF_VERSION}/verapdf-greenfield-${VERAPDF_VERSION}.${VERAPDF_PATCH_VERSION}-installer.zip" \
      -o verapdf-installer.zip \
    && unzip -q verapdf-installer.zip \
    && java -jar \
      "verapdf-greenfield-${VERAPDF_VERSION}.${VERAPDF_PATCH_VERSION}/verapdf-izpack-installer-${VERAPDF_VERSION}.${VERAPDF_PATCH_VERSION}.jar" \
      /tmp/docker-install.xml

FROM python:3.13-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VERAPDF_PATH=/opt/verapdf/verapdf \
    SCAN_TEMP_DIR=/scan-tmp \
    TMPDIR=/scan-tmp

RUN apt-get update \
    && apt-get install -y --no-install-recommends openjdk-17-jre-headless \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 10001 checker \
    && useradd --uid 10001 --gid checker --create-home --shell /usr/sbin/nologin checker \
    && mkdir -p /app /scan-tmp \
    && chown -R checker:checker /app /scan-tmp

COPY --from=verapdf-installer /opt/verapdf /opt/verapdf

# Generate installation defaults while the image is writable. At runtime veraPDF's
# user configuration and Java temporary files are redirected to RAM-backed /scan-tmp.
RUN /opt/verapdf/verapdf --version >/tmp/verapdf-version.txt \
    && test -s /tmp/verapdf-version.txt \
    && test -f /opt/verapdf/config/app.xml \
    && test -f /opt/verapdf/config/validator.xml \
    && rm -f /tmp/verapdf-version.txt

ENV HOME=/scan-tmp \
    JAVA_OPTS="-Duser.home=/scan-tmp -Djava.io.tmpdir=/scan-tmp"

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app

USER 10001:10001
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health', timeout=3)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1", "--no-access-log"]
