#
# php-cli Dockerfile
#

# Pull base image.
FROM dockerfile/ubintu

# Install Python.
RUN \
  apt-get update && \
  apt-get -y install php5-cli php5-mysql

# Set timezone 
RUN \ 
  echo 'America/Montreal'  > /etc/timezone && \
  dpkg-reconfigure --frontend noninteractive tzdata


VOLUME ["/src"]

# Define working directory.
WORKDIR /src

# Define default command.
CMD ["bash"]