FROM python:3.10

LABEL maintainer="Alireza Sharifikia"
LABEL maintainer_email="alireza.sharifikia@gmail.com"

WORKDIR ${CONTAINER_WORKSPACE}

COPY . .

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update
RUN pip install --upgrade pip
RUN pip install -r conf/requirements.txt

RUN sed -i 's/\r$//g' conf/containers/dev/py/entrypoint.sh
RUN chmod +x conf/containers/dev/py/entrypoint.sh

ENTRYPOINT [ "conf/containers/dev/py/entrypoint.sh" ]