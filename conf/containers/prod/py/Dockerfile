FROM python:3.10

LABEL maintainer="Alireza Sharifikia"
LABEL maintainer_email="alireza.sharifikia@gmail.com"

WORKDIR /home/www

COPY . .

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install flake8==6.0.0
# The following flake8 formatting rules are ignored:
# E501: Line is too long
# W504: Line break after binary operator => To be able to use multiline conditions
RUN flake8 --ignore=E501,E704,E402,W504 /home/www
RUN apt-get update
RUN pip install --upgrade pip
RUN pip install -r conf/requirements.txt

CMD [ "tail", "-f", "/dev/null" ]