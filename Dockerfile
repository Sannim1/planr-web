FROM python:2.7

MAINTAINER Abdulmusawwir Sanni<abdulmusawwir.sanni.16@ucl.ac.uk>

RUN mkdir /code
WORKDIR /code
ADD . /code/

RUN pip install -r requirements.txt
RUN pip install deap

EXPOSE 8080
CMD ["python", "/code/run.py"]
