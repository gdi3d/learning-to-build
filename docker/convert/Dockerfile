FROM python:3.8-alpine

RUN apk upgrade -U \ 
    && apk add --no-cache ca-certificates ffmpeg libva-intel-driver gcc

# crate a non-root user
# and set workdir
ARG DF_USER=youtubemp3
ARG DF_UID=1000
ENV SF_USER ${DF_USER}
ENV SF_UID ${DF_UID}
ENV HOME /app
ENV PYTHONPATH ${HOME}
ENV PATH ${PATH}:${HOME}/.local/bin

RUN adduser --disabled-password \
    --gecos "Default user" \
    --uid ${SF_UID} \
    ${SF_USER}

RUN mkdir /data && chown ${SF_USER} /data
# This dir should be the mounting point
WORKDIR ${HOME}
COPY app/convert ${HOME}/convert
COPY docker/convert/requirements.txt requirements.txt
USER root
RUN chown -R ${SF_USER}:${SF_USER} ${HOME}
RUN chmod 777 ${HOME}
USER ${SF_USER}

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN rm requirements.txt

CMD [ "celery", "-A", "convert.tasks.task", "worker", "--loglevel=INFO" ]