#
# ted1k Docker image shared by all containers (php,python,shell scripts)
#  feeds.php was ported to PHP7

# Use official docker python image
#  https://hub.docker.com/_/python/
#

# As of python:2.7.16, this would be buildpack-deps:buster based image 
#  moving past 2.7.15 breaks MySQL-python==1.2.5 requirement
FROM python:2.7.15

# Set timezone 
RUN \ 
  echo 'America/Montreal'  > /etc/timezone && \
  dpkg-reconfigure --frontend noninteractive tzdata

# Install Python Dependacies (non pip)
RUN \
  apt-get update && \
  DEBIAN_FRONTEND=noninteractive apt-get install -y \
  build-essential \
  curl \
  default-libmysqlclient-dev \
  default-mysql-client \
  php-cli \
  php-mysql \
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