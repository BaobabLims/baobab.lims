FROM plone:4.3.11

LABEL MAINTAINERS="thoba@sanbi.ac.za and hocine@sanbi.ac.za"

USER root
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends sudo build-essential \
    libffi-dev git gcc libc6-dev gcc-multilib libjpeg-dev zlib1g-dev \
    libcairo2-dev pango1.0-tests \
    # Add plone to sudoers
    && usermod -aG sudo plone

USER plone
# Clone baobablims repositories 
RUN git clone https://github.com/BaobabLims/baobab.lims.git \
    && git clone https://github.com/BaobabLims/bika.lims.git \
    && git clone https://github.com/BaobabLims/graphite.theme.git

COPY buildout.cfg /plone/instance/buildout.cfg
RUN sudo -u plone bin/buildout -n
