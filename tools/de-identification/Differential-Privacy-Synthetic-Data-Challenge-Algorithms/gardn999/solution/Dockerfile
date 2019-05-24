
FROM ubuntu:16.04

## Install General Requirements
RUN apt-get update && \
    apt-get install -y openjdk-8-jdk && \
    apt-get install -y --no-install-recommends \
    apt-utils \
    build-essential \
    cmake \
    git \
    wget \
    nano \
    software-properties-common
		
WORKDIR /x

# copy entire directory where docker file is into docker container at /work
COPY . /x/

RUN chmod 777 run.sh

ENTRYPOINT [ "/x/run.sh" ]
