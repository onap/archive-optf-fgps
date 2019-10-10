FROM python:2.7.15-alpine

COPY 	/src/ /opt/engine
WORKDIR /opt/engine

ARG HTTP_PROXY
ARG HTTPS_PROXY

ENV HTTP_PROXY ${HTTP_PROXY}
ENV HTTPS_PROXY ${HTTPS_PROXY}

RUN apk --update add --virtual build-dep gcc musl-dev linux-headers libc-dev \
 && pip install -r requirements.txt \
 && apk del build-dep

ENV HTTP_PROXY ""
ENV HTTPS_PROXY ""

RUN addgroup -g 825 -S valetg && adduser -u 825 -S valetu -G valetg && chown -R valetu:valetg /opt/engine
USER valetu:valetg
RUN date > /home/valetu/imagedate.txt

CMD ["python", "valet/valet_main.py", "/opt/config/solver.json"]


