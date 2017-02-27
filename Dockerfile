FROM tiangolo/uwsgi-nginx:python2.7

MAINTAINER Abdulmusawwir Sanni<abdulmusawwir.sanni.16@ucl.ac.uk>

COPY requirements.txt /tmp/

# Remove deap from requirements.txt (always causes error during pip install)
RUN sed -i "/.*deap==.*/d" /tmp/requirements.txt

# Install dependencies and manually install "deap"
RUN pip install -r /tmp/requirements.txt \
    && pip install deap

# Add Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/

# Copy flask app and configuration into image
COPY main.py /app/main.py
COPY config.py /app/config.py
COPY ./app /app/app
