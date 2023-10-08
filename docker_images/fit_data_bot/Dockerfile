FROM ubuntu:latest

COPY ../../fit_data_bot ./fit_data_bot

RUN pip install -r ./fit_data_bot/packages

CMD ["python", "./fit_data_bot/main.py"]