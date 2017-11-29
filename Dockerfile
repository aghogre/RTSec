FROM alpine:3.6

ARG LIBRDKAFKA_NAME="librdkafka"
ARG LIBRDKAFKA_VER="0.9.5"

RUN  apk add --no-cache --update bash && \
     apk add python py-pip gcc python-dev build-base g++ musl-dev tar ca-certificates openssl && \
     pip install --upgrade pip

RUN BUILD_DIR="$(mktemp -d)" && \
    wget -O "$BUILD_DIR/$LIBRDKAFKA_NAME.tar.gz" "https://github.com/edenhill/librdkafka/archive/v$LIBRDKAFKA_VER.tar.gz" && \
    mkdir -p $BUILD_DIR/$LIBRDKAFKA_NAME-$LIBRDKAFKA_VER && \
    tar \
      --extract \
      --file "$BUILD_DIR/$LIBRDKAFKA_NAME.tar.gz" \
      --directory "$BUILD_DIR/$LIBRDKAFKA_NAME-$LIBRDKAFKA_VER" \
      --strip-components 1 && \
    cd "$BUILD_DIR/$LIBRDKAFKA_NAME-$LIBRDKAFKA_VER" && \
    ./configure --prefix=/usr && \
    make -j && \
    make install

ADD . /TWITTERCONSUMER

WORKDIR /TWITTERCONSUMER

RUN pip install -r requirements.txt

CMD ["/bin/bash", "-c", "source arguments.env && python TwitterConsumerStreaming.py"]