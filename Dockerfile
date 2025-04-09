FROM python:3.8-slim-buster
LABEL maintainer = "Webank CTB Team"
# Install logrotate
RUN sed -i 's/deb.debian.org/mirrors.tencentyun.com/g' /etc/apt/sources.list
RUN sed -i 's/security.debian.org/mirrors.tencentyun.com/g' /etc/apt/sources.list
COPY api/terminal/requirements.txt /tmp/requirements.txt
COPY api/terminal/dist/* /tmp/
# Install && Clean up
RUN apt update && apt-get -y install gcc python3-dev swig libssl-dev && \
    pip3 install -i http://mirrors.tencentyun.com/pypi/simple/ --trusted-host mirrors.tencentyun.com -r /tmp/requirements.txt && \
    pip3 install /tmp/*.whl && \
    rm -rf /root/.cache && apt autoclean && \
    rm -rf /tmp/* /var/lib/apt/* /var/cache/* && \
    apt purge -y `cat /var/log/apt/history.log|grep 'Install: '|tail -1| sed 's/Install://'| sed 's/\ /\n/g' | sed '/(/d' | sed '/)/d' | sed ':l;N;s/\n/ /;b l'`
# Add ssh client & telnet command for user to test
RUN apt update && apt -y install openssh-client telnet && rm -rf /root/.cache && apt autoclean && \
    rm -rf /tmp/* /var/lib/apt/* /var/cache/*
# Use app:app to run gunicorn
RUN mkdir -p /etc/terminal/
RUN mkdir -p /var/log/terminal/
RUN mkdir -p /data/terminal/records
RUN mkdir -p /data/terminal/ui
RUN echo "It works" > /data/terminal/ui/index.html
COPY api/terminal/etc /etc/terminal
COPY build/start_all.sh /scripts/start_all.sh
RUN chmod +x /scripts/start_all.sh

RUN addgroup --system --gid 6000 apps && useradd --uid 6001 --gid 6000 app
RUN chown -R app:apps /etc/terminal && chown -R app:apps /var/log/terminal && chown -R app:apps /data/terminal && chown -R app:apps /scripts
RUN chmod -R 755 /etc/terminal && chmod -R 755 /var/log/terminal && chmod -R 755 /data/terminal && chmod -R 755 /scripts
USER app
ENTRYPOINT ["/bin/sh", "/scripts/start_all.sh"]
