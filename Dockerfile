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

# Set timezone ?
# ZZ='America/Montreal'; [ $ZZ = `cat /etc/timezone` ] || (echo $ZZ > /etc/timezone; sudo dpkg-reconfigure --frontend noninteractive tzdata)

# Add our code (.dockerignore)
ADD . /src

# Define mountable directories.
VOLUME ["/data"]

# Define working directory.
WORKDIR /src

# Define default command.
CMD ["bash"]