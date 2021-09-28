FROM plone:4.3.19

LABEL MAINTAINERS="support@baobablims.org"

USER root
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends sudo build-essential \
    libffi-dev git gcc libc6-dev gcc-multilib libjpeg-dev zlib1g-dev \
    libcairo2-dev pango1.0-tests python-minimal \
    # Add plone to sudoers
    && usermod -aG sudo plone

USER plone

# Clone baobablims repositories 
RUN git clone https://github.com/BaobabLims/baobab.lims.git \
    && git clone https://github.com/BaobabLims/bika.lims.git \
    && git clone https://github.com/BaobabLims/graphite.theme.git

WORKDIR /baobab.lims
COPY buildout.cfg /plone/instance/buildout.cfg

RUN pip install zc.buildout

RUN echo $(ls -1 /baobab.lims)
WORKDIR /plone/instance/
RUN sudo -u plone buildout -n
