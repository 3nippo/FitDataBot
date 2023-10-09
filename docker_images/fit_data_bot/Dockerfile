FROM ubuntu:latest

env FIT_DATA_BOT_PATH=/usr/bin/fit_data_bot

COPY ./fit_data_bot $FIT_DATA_BOT_PATH

RUN apt-get update && apt-get install -y python3-pip
RUN pip3 install -r $FIT_DATA_BOT_PATH/packages
RUN pip3 install "psycopg[binary,pool]"

CMD ["python3", "/usr/bin/fit_data_bot/main.py"]