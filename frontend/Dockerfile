# Dockerfile for PHP 7 mysqli


FROM php:7.4-apache-buster

#RUN curl -sL https://deb.nodesource.com/setup_12.x | bash -

RUN apt-get -y update && \
    apt-get -y install \
      pkg-config \
      nodejs npm git


RUN docker-php-ext-install mysqli
EXPOSE 80
WORKDIR /app/html

RUN npm install -g bower  gulp

RUN bower --allow-root install \
    bootstrap#3.4.1 \
    bootstrap-treeview \
    patternfly-bootstrap-treeview#2.1.5 \
    d3#4.1.1 \
    moment \
    moment-timezone \
    jquery-confirm \
    bootstrap-combobox \
    bootstrap-table \
    bootstrap-toggle \
    progressbar.js \
    bootstrap-select \
    jquery-confirm2 \
    eonasdan-bootstrap-datetimepicker

RUN npm install @json-editor/json-editor@1.2.1 hls.js gulp gulp-concat gulp-rename gulp-uglify  gulp-sourcemaps
COPY . /var/www/html