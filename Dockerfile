# Invoke with docker run -p 8000:80 <dockerimageid>
# Then use by browsing http://localhost:8000
FROM debian:9
MAINTAINER bruno.cornec@hpe.com
ENV DEBIAN_FRONTEND noninterative
# Install deps for Redfish mockup
RUN apt-get update
RUN apt-get -y install apache2 unzip sed patch vim wget iproute2 python3 python3-requests
ENV MODELPORT=$MODELPORT
EXPOSE $MODELPORT
RUN mkdir -p /mockup
COPY redfishMockupServer.py /mockup
COPY rfSsdpServer.py /mockup
COPY run-mockup.sh /mockup
CMD /mockup/run-mockup.sh
