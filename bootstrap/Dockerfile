FROM python:3-alpine

RUN apk add --no-cache libffi openssl vim

RUN apk add --no-cache --virtual .build-deps \
        bash curl tar gcc libc-dev libffi-dev \
        linux-headers make python3-dev

WORKDIR /app
COPY app/requirements.txt /app/
RUN pip3 --no-cache-dir install --upgrade pip && \
    pip3 --no-cache-dir install -r /app/requirements.txt --upgrade

COPY app /app
RUN rm -rf ~/.pip/cache $PWD/build/; \
    ln -s /data

RUN apk del .build-deps && rm -rf ~/.cache

CMD ["/app/oz-aws-bootstrap"]
