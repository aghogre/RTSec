FROM c12e/alpine-miniconda:conda-4.3.14

RUN  apk add --no-cache --update bash

RUN apk add --update \
    python \
    python-dev \
    py-pip \
    build-base

ADD . /FINANCIALNEWSDATA

WORKDIR /FINANCIALNEWSDATA

RUN apk add python-dev curl libxml2-dev libxslt-dev libffi-dev gcc musl-dev libgcc openssl-dev

RUN pip install -r requirements.txt
RUN conda config --add channels conda-forge


CMD ["/bin/bash", "-c", "source arguments.env && python FinancialDataExtractor.py"]
