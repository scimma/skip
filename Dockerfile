FROM python:3.8
MAINTAINER David Collom <dcollom@lco.global>

RUN apt-get update && apt-get install -y gdal-bin libproj-dev

EXPOSE 8080
ENTRYPOINT ["/usr/local/bin/gunicorn", "app:app", "--bind=0.0.0.0:8080"]
WORKDIR /skip

COPY requirements.txt /skip

RUN pip install --upgrade pip && pip --no-cache-dir install gunicorn[gevent] -r /skip/requirements.txt

COPY . /skip