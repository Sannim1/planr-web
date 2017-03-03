# tiangolo/uwsgi-nginx:python2.7 requires that the uwsgi application callable
# resides in `main.py` and is named `application`
from app import app as application
