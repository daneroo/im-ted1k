#
# Python Dockerfile
#
# https://github.com/dockerfile/python
#

# Pull base image.
FROM dockerfile/python

# Install Python.
RUN \
  apt-get update && \
  apt-get -y install python-mysqldb python-serial mysql-client

# Set timezone 
RUN \ 
  echo 'America/Montreal'  > /etc/timezone && \
  dpkg-reconfigure --frontend noninteractive tzdata

# Force stdin, stdout and stderr to be totally unbuffered
ENV PYTHONUNBUFFERED 1

# Add our code (.dockerignore)
ADD . /src

# Define mountable directories.
VOLUME ["/data"]

# Define working directory.
WORKDIR /src

# Define default command.
CMD ["bash"]