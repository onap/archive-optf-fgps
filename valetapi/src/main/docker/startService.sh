#!/bin/sh
touch /app.jar

java \
 -Dloader.path=/opt/etc/config/,/opt/bin/app.jar \
 -Dlogging.config=file:/opt/etc/config/logback.xml \
 -Dspring.config.location=file:/opt/etc/config/application.properties,/opt/etc/config/auth.properties,/opt/etc/config/key.properties,/opt/etc/config/resources.properties,/opt/etc/config/version.properties \
 $java_runtime_arguments \
 -jar /opt/bin/app.jar
