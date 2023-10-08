FROM postgres:latest

RUN apt-get update && apt-get -y install cron

COPY ./backup_db_cron /etc/cron.d/backup_db_cron
RUN chmod 644 /etc/cron.d/backup_db_cron

COPY ./backup.sh /usr/bin/backup.sh
RUN chmod 744 /usr/bin/backup.sh

RUN crontab /etc/cron.d/backup_db_cron

CMD ["cron", "-f"]