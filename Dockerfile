#
# ted1k Docker image shared by all containers (php,python,shell scripts)
# Use official docker python image
#  https://hub.docker.com/_/python/
#

# Pull base image.
# Now using pip/requirements not ubuntu packages for python: 
# FROM python:2.7
FROM hypriot/rpi-python

# Set timezone 
RUN \ 
  echo 'America/Montreal'  > /etc/timezone && \
  dpkg-reconfigure --frontend noninteractive tzdata

# Install Python Dependacies (non pip)
RUN \
  apt-get update && \
  DEBIAN_FRONTEND=noninteractive apt-get install -y \
	build-essential \
	libmysqlclient-dev \
	mysql-client \
	php5-cli \
	php5-mysql \
	python-dev

# Add our pip dependancy file
ADD src/requirements.txt /src/requirements.txt

# Install python packages (relative to WORKDIR)
RUN \
  pip install -r /src/requirements.txt

# Force stdin, stdout and stderr to be totally unbuffered
ENV PYTHONUNBUFFERED 1

# Add our code (.dockerignore)
ADD src /src

# Define working directory.
WORKDIR /src

# Define mountable directories.
VOLUME ["/data"]

# Define default command.
CMD ["bash"]