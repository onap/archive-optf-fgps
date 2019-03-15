FROM openjdk:8-jre-alpine

RUN addgroup -g 825 -S valetg && adduser -u 825 -S valetu -G valetg
RUN mkdir -p /opt/logs/valet/api && chown -R valetu:valetg /opt/logs

VOLUME /tmp
VOLUME /opt/etc
VOLUME /opt/bin
VOLUME /opt/logs

ADD ValetApi.jar /opt/bin/app.jar
ADD startService.sh /startService.sh

RUN chown valetu:valetg /startService.sh
USER valetu:valetg
RUN chmod 700 /startService.sh && date > /home/valetu/imagedate.txt

ENTRYPOINT ./startService.sh
