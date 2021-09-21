FROM python:3.8
MAINTAINER David Collom <dcollom@lco.global>

RUN apt-get update && apt-get install -y gdal-bin libproj-dev

EXPOSE 8080
ENTRYPOINT ["/usr/local/bin/gunicorn", "skip_base.wsgi:application", "--bind=0.0.0.0:80"]
WORKDIR /skip

COPY requirements.txt /skip

RUN pip install --upgrade pip && pip --no-cache-dir install gunicorn[gevent] -r /skip/requirements.txt

COPY . /skip

# continue to setup the image with node and npm install (via nvm)
# see https://stackoverflow.com/questions/25899912/

# Use bash for subsequent RUN, CMD, ENTRYPOINT commands
SHELL ["/bin/bash", "--login", "-c"]

ENV NVM_DIR /usr/local/nvm
RUN mkdir -p $NVM_DIR
ENV NODE_VERSION 14.17.0

# Install nvm with node and npm
RUN curl https://raw.githubusercontent.com/creationix/nvm/v0.38.0/install.sh | bash \
    && source $NVM_DIR/nvm.sh \
    && nvm install $NODE_VERSION \
    && nvm alias default $NODE_VERSION \
    && nvm use default

ENV NODE_PATH $NVM_DIR/v$NODE_VERSION/lib/node_modules
ENV PATH      $NVM_DIR/versions/node/v$NODE_VERSION/bin:$PATH

# write new webpack-stats.json for django-webpack-loader to use
# and install the Vue JS/CSS etc as static files
WORKDIR /skip/vue
RUN npm install && npm run build

WORKDIR /skip

RUN python manage.py collectstatic --noinput