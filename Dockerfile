FROM ubuntu:24.04
LABEL org.opencontainers.image.source="https://github.com/DataFog/fogmachine"
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends build-essential ca-certificates curl git libssl-dev pkg-config python3 python3-dev python3-venv sudo xz-utils && rm -rf /var/lib/apt/lists/*
COPY toolchains.json /opt/fogmachine/toolchains.json
COPY scripts/pin.py /opt/fogmachine/scripts/pin.py
RUN NODE_MAJOR=$(python3 /opt/fogmachine/scripts/pin.py node_major) && curl -fsSL https://deb.nodesource.com/setup_${NODE_MAJOR}.x -o /tmp/node-setup.sh && bash /tmp/node-setup.sh && apt-get install -y nodejs && rm -rf /var/lib/apt/lists/* /tmp/node-setup.sh
RUN usermod -aG sudo ubuntu && echo 'ubuntu ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/ubuntu
USER ubuntu
ENV PATH="/home/ubuntu/.cargo/bin:/home/ubuntu/.local/bin:${PATH}"
RUN RUST_VERSION=$(python3 /opt/fogmachine/scripts/pin.py rust) && curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs -o /tmp/rustup.sh && sh /tmp/rustup.sh -y --default-toolchain "$RUST_VERSION" --profile minimal --component rustfmt --component clippy && rm /tmp/rustup.sh && rustup target add wasm32-unknown-unknown
RUN UV_VERSION=$(python3 /opt/fogmachine/scripts/pin.py uv) && curl -LsSf "https://astral.sh/uv/$UV_VERSION/install.sh" -o /tmp/uv.sh && sh /tmp/uv.sh && rm /tmp/uv.sh
RUN python3 -m venv /home/ubuntu/.fogmachine-python && uv pip install --python /home/ubuntu/.fogmachine-python/bin/python "maturin==$(python3 /opt/fogmachine/scripts/pin.py maturin)"
ENV PATH="/home/ubuntu/.fogmachine-python/bin:${PATH}"
RUN cargo install wasm-bindgen-cli --version "$(python3 /opt/fogmachine/scripts/pin.py wasm_bindgen)" --locked
USER root
RUN mkdir -p /opt/fogmachine/browser /workspace && chown -R ubuntu:ubuntu /opt/fogmachine/browser /workspace
USER ubuntu
RUN cd /opt/fogmachine/browser && npm install --save-exact "playwright@$(python3 /opt/fogmachine/scripts/pin.py playwright)" && npx playwright install --with-deps chromium
COPY --chown=ubuntu:ubuntu dev /opt/fogmachine/dev
WORKDIR /workspace
CMD ["sleep", "infinity"]
