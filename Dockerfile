FROM alpine:3.6

RUN apk update && \
apk add python3 postgresql-libs && \
apk add --virtual .build-deps gcc python3-dev musl-dev postgresql-dev && \
apk --purge del .build-deps

ADD . /SQL-DBMigration

WORKDIR /SQL-DBMigration
RUN pip install -r requirements.txt

CMD ["/bin/bash", "-c", "source arguments.env && python thomsonDBMigrn.py"]
