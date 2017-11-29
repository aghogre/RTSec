FROM c12e/alpine-miniconda:conda-4.3.14

RUN  apk add --no-cache --update bash

RUN apk add --update \
    python \
    python-dev \
    py-pip \
    build-base

ADD . /TWITTERPRODUCER

WORKDIR /TWITTERPRODUCER

RUN pip install -r requirements.txt
RUN conda config --add channels conda-forge
RUN conda install --yes --file conda_requirements.txt


CMD ["/bin/bash", "-c", "source arguments.env && python TwitterProducerStreaming.py"]

