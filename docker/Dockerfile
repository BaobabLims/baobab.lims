FROM continuumio/miniconda2

RUN apt-get update --allow-releaseinfo-change

RUN apt-get install -y wget build-essential libxml2 libxml2-dev \
    libxslt1.1 libxslt1-dev libffi-dev libcairo2 libpango-1.0-0 \
    libgdk-pixbuf2.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 zlib1g zlib1g-dev \
    libssl-dev python2.7 python2.7-dev

RUN useradd -m -s /bin/bash baobab

RUN chown -R baobab:baobab /opt/conda 

USER baobab

RUN echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc 

SHELL ["/bin/bash", "--login", "-c"]

RUN conda create -n baobab -y python=2.7 

RUN echo "conda activate baobab" >> ~/.bashrc

WORKDIR /home/baobab

RUN wget --no-check-certificate https://launchpad.net/plone/4.3/4.3.19/+download/Plone-4.3.19-UnifiedInstaller.tgz && tar xf Plone-4.3.19-UnifiedInstaller.tgz

RUN cd Plone-4.3.19-UnifiedInstaller && ./install.sh standalone --target=/home/baobab --instance=baobablims --password=admin

COPY buildout.cfg.patch /home/baobab/buildout.cfg.patch

WORKDIR /home/baobab/baobablims

RUN patch <~/buildout.cfg.patch

RUN cd src && git clone https://github.com/BaobabLims/bika.lims.git && \
    git clone https://github.com/BaobabLims/baobab.lims.git && \
    git clone https://github.com/BaobabLims/graphite.theme.git

COPY requirements.txt /home/baobab/baobablims/requirements.txt

RUN conda activate baobab && pip install -r requirements.txt

RUN conda activate baobab && PYTHONHTTPSVERIFY=0 buildout

COPY run_server.sh /home/baobab/baobablims

ENTRYPOINT ["/bin/bash", "/home/baobab/baobablims/run_server.sh"]
