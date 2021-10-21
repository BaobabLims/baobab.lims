FROM python:2.7-alpine

ENV PIP=9.0.3 \
    ZC_BUILDOUT=2.13.1 \
    SETUPTOOLS=40.8.0 \
    WHEEL=0.33.1 \
    PLONE_MAJOR=4.3 \
    PLONE_VERSION=4.3.19 \
    PLONE_MD5=04ed5beac7fb8504f06a36d44e407b06

LABEL plone=$PLONE_VERSION \
    os="alpine" \
    os.version="3.10" \
    name="Plone 4.3" \
    description="Plone image, based on Unified Installer" \
    maintainer="Plone Community"

RUN addgroup -g 500 plone \
 && adduser -S -D -G plone -u 500 plone \
 && mkdir -p /plone/instance /data/filestorage /data/blobstorage

COPY buildout.cfg /plone/instance/
COPY baobab-lims-buildout.cfg /plone/instance/

RUN apk add --no-cache --virtual .build-deps \
    gcc \
    libc-dev \
    zlib-dev \
    libjpeg-turbo-dev \
    libpng-dev \
    libxml2-dev \
    libxslt-dev \
    pcre-dev \
    bash \
    sudo \
    su-exec \
    libjpeg-turbo \
 && apk add git \
 && apk add --no-cache git make bash \
 && wget -O Plone.tgz https://launchpad.net/plone/$PLONE_MAJOR/$PLONE_VERSION/+download/Plone-$PLONE_VERSION-UnifiedInstaller.tgz \
 && echo "$PLONE_MD5  Plone.tgz" | md5sum -c - \
 && tar -zxvf Plone.tgz \
 && cp -rv ./Plone-$PLONE_VERSION-UnifiedInstaller/base_skeleton/* /plone/instance/ \
 && cp -v ./Plone-$PLONE_VERSION-UnifiedInstaller/buildout_templates/buildout.cfg /plone/instance/buildout-base.cfg \
 && pip install pip==$PIP setuptools==$SETUPTOOLS zc.buildout==$ZC_BUILDOUT wheel==$WHEEL \
 && pip install zope.testbrowser==3.11.1 \
 && pip install lxml \
 && pip install zope.processlifetime \
 && cd /plone/instance \
 && buildout \
 && rm -rf bin/buildout \
 && ln -s /data/filestorage/ /plone/instance/var/filestorage \
 && ln -s /data/blobstorage /plone/instance//var/blobstorage \
 && find /data  -not -user plone -exec chown plone:plone {} \+ \
 && find /plone -not -user plone -exec chown plone:plone {} \+ \
 && rm -rf /Plone* \
 && apk del .build-deps \
 && apk add --no-cache --virtual .run-deps \
    su-exec \
    bash \
    openssh \
    git \
    #bzip-devel \
    rsync \
    libxml2 \
    libxslt \
    libjpeg-turbo \
 && rm -rf /plone/buildout-cache/downloads/*



VOLUME /data
COPY docker-initialize.py docker-entrypoint.sh /

EXPOSE 8080
WORKDIR /plone/instance

RUN mkdir -p var/log/
RUN touch /plone/instance/var/log/instance.log

HEALTHCHECK --interval=1m --timeout=5s --start-period=1m \
  CMD nc -z -w5 127.0.0.1 8080 || exit 1

RUN ["chmod", "+x", "/docker-entrypoint.sh"]

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["start"]