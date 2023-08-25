FROM python:3

RUN mkdir -p /opt/src/application

COPY application/configurationStore.py /opt/src/application/configurationStore.py
COPY application/migrate.py /opt/src/application/migrate.py
COPY application/modelsStore.py /opt/src/application/modelsStore.py
COPY requirements.txt /opt/src/application/requirements.txt

RUN pip install -r /opt/src/application/requirements.txt

ENV PYTHONPATH="/opt/src/application"

ENTRYPOINT ["python", "/opt/src/application/migrate.py"]