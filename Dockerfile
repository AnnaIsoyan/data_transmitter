FROM python:3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create app directory
WORKDIR /data/www/data_transmitter

# create tooltip directories
RUN mkdir -p /data/storages && mkdir -p /data/www/data_transmitter/var/log
RUN chmod -R 777 /data/storages && chmod -R 777 /data/www/data_transmitter/var

# install dependencies:
COPY requirements.txt /data/www/data_transmitter
RUN pip --no-cache-dir install -r requirements.txt

# bundle app source
COPY . /data/www/data_transmitter
