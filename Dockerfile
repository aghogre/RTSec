FROM continuumio/anaconda:4.4.0

ADD . /SQL-DBMigration

WORKDIR /SQL-DBMigration

RUN conda config --add channels conda-forge
RUN conda install --yes --file requirements.txt

CMD ["/bin/bash", "-c", "source arguments.env && python thomsonDBMigrn.py"]
