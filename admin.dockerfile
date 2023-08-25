FROM python:3

RUN mkdir -p /opt/src/application

COPY application/configurationStore.py /opt/src/application/configurationStore.py
COPY decorator.py /opt/src/application/decorator.py
COPY application/admin.py /opt/src/application/admin.py
COPY application/manageStore.py /opt/src/application/manageStore.py
COPY application/modelsStore.py /opt/src/application/modelsStore.py
COPY requirements.txt /opt/src/application/requirements.txt

RUN pip install -r /opt/src/application/requirements.txt

ENV PYTHONPATH="/opt/src/application"

ENTRYPOINT ["python", "/opt/src/application/admin.py"]