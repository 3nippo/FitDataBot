FROM postgres:latest

RUN apt-get update && apt-get -y install curl jq

RUN mkdir -p /docker-entrypoint-initdb.d

ENV RESTORE_SH_PATH=/docker-entrypoint-initdb.d/restore_backup.sh
COPY ./restore_backup.sh $RESTORE_SH_PATH
RUN chmod 744 $RESTORE_SH_PATH