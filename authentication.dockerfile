FROM python:3

RUN mkdir -p /opt/src/authentication

COPY authentication/configurationUsers.py /opt/src/authentication/configurationUsers.py
COPY decorator.py /opt/src/authentication/decorator.py
COPY authentication/authentication.py /opt/src/authentication/authentication.py
COPY authentication/manageUsers.py /opt/src/authentication/manageUsers.py
COPY authentication/modelsUsers.py /opt/src/authentication/modelsUsers.py
COPY requirements.txt /opt/src/authentication/requirements.txt

RUN pip install -r /opt/src/authentication/requirements.txt

ENV PYTHONPATH="/opt/src/authentication"

ENTRYPOINT ["python", "/opt/src/authentication/authentication.py"]