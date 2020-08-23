FROM python:3.7-slim

RUN apt-get clean && apt-get update && apt-get install -y --no-install-recommends \
	git \
	gcc \
	libpng-dev \
	libfreetype6-dev \
	libopenblas-dev \
	liblapack-dev \
	libatlas-base-dev \
	libssl-dev \
	libhdf5-dev \
	&& git clone --branch v3.0-devel --depth 1 \
	http://jro-dev.igp.gob.pe/rhodecode/schain \
	&& pip install numpy \
	&& cd schain \
	&& pip install . \
	&& rm -rf * \
	&& apt-get purge -y --auto-remove git gcc \
	&& rm -rf /var/lib/apt/lists/*

ENV BACKEND="Agg"

VOLUME /data

ENTRYPOINT ["schain"]
