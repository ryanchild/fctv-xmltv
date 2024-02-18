FROM python:3.10-alpine

ADD src/ /app/

WORKDIR /app

RUN apk update && \
    apk add bash

RUN pip install -r /app/requirements.txt

RUN echo $HOME

ENTRYPOINT ["/app/run.sh"]
