#
# ted1k Docker image shared by all containers (php,python,shell scripts)
# Use official docker python image
#  https://hub.docker.com/_/python/
#

# Pull base image.
# Now using pip/requirements not ubuntu packages for python: 
# FROM dockerfile/python
FROM python:2.7

# Install Python.
RUN \
  apt-get update && \
  DEBIAN_FRONTEND=noninteractive apt-get install -y mysql-client php5-cli php5-mysql

# Set timezone 
RUN \ 
  echo 'America/Montreal'  > /etc/timezone && \
  dpkg-reconfigure --frontend noninteractive tzdata

# Force stdin, stdout and stderr to be totally unbuffered
ENV PYTHONUNBUFFERED 1

# Add our code (.dockerignore)
ADD src /src

# Define working directory.
WORKDIR /src

# Install python packages (relative to WORKDIR)
RUN \
  pip install --no-cache-dir -r requirements.txt

# Define mountable directories.
VOLUME ["/data"]

# Define default command.
CMD ["bash"]