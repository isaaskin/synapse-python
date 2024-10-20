FROM debian:bookworm-slim

RUN apt update && apt install -y --no-install-recommends \
    make \
    python3 \
    python3-pip \
    python3-poetry
