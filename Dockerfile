FROM python:3.10

ENV DOWNLOAD_URL_BASE=https://github.com/rhasspy/piper/releases/download/2023.11.14-2/
ENV PIPER_HOME=/piper
RUN apt-get update && apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*
# Download and extract Piper binaries
RUN dpkgArch="$(dpkg --print-architecture)" && \
    case "${dpkgArch##*-}" in \
        amd64) DOWNLOAD_URL=${DOWNLOAD_URL_BASE}piper_linux_x86_64.tar.gz ;; \
        armhf) DOWNLOAD_URL=${DOWNLOAD_URL_BASE}piper_linux_armv7l.tar.gz ;; \
        arm64) DOWNLOAD_URL=${DOWNLOAD_URL_BASE}piper_linux_aarch64.tar.gz ;; \
        *) echo "Unsupported architecture: ${dpkgArch}"; exit 1 ;; \
    esac && \
    curl -SL ${DOWNLOAD_URL} | tar -xzC /tmp && \
    mv /tmp/piper/* /usr/bin/ && \
    chmod +x /usr/bin/* && \
    rm -rf /tmp/piper
# Set working directory
WORKDIR $PIPER_HOME
# Copy necessary files
COPY ./models/ $PIPER_HOME/models/
COPY ./piper.py $PIPER_HOME/piper.py
# Download ONNX models (Optional uwu)
RUN wget https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_MX/claude/high/es_MX-claude-high.onnx -O $PIPER_HOME/models/es_MX-claude-14947-epoch-high.onnx && \
    wget https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_MX/claude/high/es_MX-claude-high.onnx.json -O $PIPER_HOME/models/es_MX-claude-14947-epoch-high.onnx.json
# Install dependencies
RUN pip install discord
# Create output directory
RUN mkdir $PIPER_HOME/output
# Run Piper bot
CMD dd if=/dev/zero of=/swapfile bs=1024 count=1048576; chmod 600 /swapfile; mkswap /swapfile; swapon /swapfile; sysctl vm.swappiness=10; echo "vm.swappiness=10" >> /etc/sysctl.conf; python3 piper.py
