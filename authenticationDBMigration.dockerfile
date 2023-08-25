FROM python:3

RUN mkdir -p /opt/src/authentication

COPY authentication/configurationUsers.py /opt/src/authentication/configurationUsers.py
COPY authentication/migrate.py /opt/src/authentication/migrate.py
COPY authentication/modelsUsers.py /opt/src/authentication/modelsUsers.py
COPY requirements.txt /opt/src/authentication/requirements.txt

RUN pip install -r /opt/src/authentication/requirements.txt

ENV PYTHONPATH="/opt/src/authentication"

ENTRYPOINT ["python", "/opt/src/authentication/migrate.py"]