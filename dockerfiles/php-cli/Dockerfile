#
# php-cli Dockerfile
#

# Pull base image.
FROM dockerfile/ubuntu

# Install Python.
RUN \
  apt-get update && \
  DEBIAN_FRONTEND=noninteractive apt-get install -y php5-cli php5-mysql

# Set timezone 
RUN \ 
  echo 'America/Montreal'  > /etc/timezone && \
  dpkg-reconfigure --frontend noninteractive tzdata

# Add our code (.dockerignore)
ADD . /src

VOLUME ["/src"]

# Define working directory.
WORKDIR /src

# Define default command.
CMD ["bash"]