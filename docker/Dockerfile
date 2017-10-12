FROM plone:4.3.11

MAINTAINER Thoba Lose 'thoba@sanbi.ac.za' and Hocine Bendou 'hocine@sanbi.ac.za'

WORKDIR /plone/instance
USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends libffi-dev git gcc libc6-dev gcc-multilib libjpeg-dev zlib1g-dev libcairo2-dev pango1.0-tests
USER plone
RUN git clone https://github.com/BaobabLims/baobab.lims.git \
    && git clone https://github.com/BaobabLims/bika.lims.git \
    && git clone https://github.com/BaobabLims/graphite.theme.git

COPY buildout.cfg /plone/instance/buildout.cfg

RUN bin/buildout -n

VOLUME /data/filestorage /data/blobstorage

COPY docker-entrypoint.sh /docker-entrypoint.shvi

USER root
RUN chmod +x /docker-entrypoint.sh

EXPOSE 8080

USER plone

ENTRYPOINT ["/docker-entrypoint.sh"]

CMD ["start"]
