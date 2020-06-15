FROM centos

VOLUME /opt

ARG user=application

WORKDIR /var/www/html

RUN yum install -y httpd unzip

ADD https://github.com/rampatra/wedding-website/archive/master.zip .

RUN unzip master.zip && mv wedding-website-master/* .

RUN useradd $user && chown $user:$user  . -R

USER $user

RUN rm -rf master.zip wedding-website-master

USER root

CMD apachectl -DFOREGROUND
