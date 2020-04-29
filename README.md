<div align="center">

  <h1>
    <a href="https://github.com/BaobabLims/baobab.lims">
      <div>
        <img src="https://baobablims.org/wp-content/uploads/2018/11/cropped-Baobab-LOGO.png" alt="senaite.lims" height="64" />
      </div>
    </a>
  </h1>

  <div>
    <!--<a href="https://pypi.python.org/pypi/senaite.lims">
      <img src="https://img.shields.io/pypi/v/senaite.lims.svg?style=flat-square" alt="pypi-version" />
    </a> -->
    <a href="https://github.com/BaobabLims/baobab.lims/pulls">
      <img src="https://img.shields.io/github/issues-pr/BaobabLims/baobab.lims.svg?style=for-the-badge" alt="open PRs" />
    </a>
    <a href="https://github.com/BaobabLims/baobab.lims/issues">
      <img src="https://img.shields.io/github/issues/BaobabLims/baobab.lims?style=for-the-badge" alt="open Issues" />
    </a>
    <a href="https://github.com/BaobabLims/baobab.lims">
      <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=for-the-badge" alt="pr" />
    </a>
    <a href="https://travis-ci.org/github/BaobabLims/baobab.lims">
       <img src="https://img.shields.io/travis/BaobabLims/baobab.lims/master?style=for-the-badge" alt="travis" />
    </a>
    <a href="https://github.com/BaobabLims/baobab.lims">
       <img src="https://img.shields.io/github/languages/top/BaobabLims/baobab.lims?style=for-the-badge" alt="language" />
    </a>
    <a href="https://github.com/BaobabLims/baobab.lims">
        <img src="https://img.shields.io/github/license/BaobabLims/baobab.lims?style=for-the-badge" alt="license" />
    </a>
    <a href="https://www.baobab.org">
      <img src="https://img.shields.io/badge/Developed%20by-SANBI-yellowgreen?style=for-the-badge" alt="Made by SANBI for LIMS Community" />
    </a>
    <a href="https://gitter.im/BaobabLims/Lobby">
      <img src="https://img.shields.io/gitter/room/BaobabLims/baobab.lims?style=for-the-badge" alt="Gitter"/>
    </a>
  </div>
</div>

# Baobab LIMS

Baobab LIMS is an open-source laboratory information management system (LIMS) software that will ensure that researchers can track the lifecycle of a biospecimen in the laboratory from receipt to storage and reuse. This software ensures that sufficient metadata is captured.

_Baobab_ is a common name given to nine tree species in different countries in the world, mostly in Africa.

Baobab LIMS written in Plone, a python framework known for its robustness, and inherits some modules from Bika LIMS.

The latest information about Baobab LIMS community can be found on the [Baobab
LIMS](https://baobablims.org/).

# QuickStart with Docker

<a href="http://play-with-docker.com?stack=https://raw.githubusercontent.com/BaobabLims/baobab.lims/master/stack.yml">
  <img src="https://img.shields.io/badge/Try%20in%20-PWD-blue?style=for-the-badge" />
</a>

Play with Docker will give 4 hours to try Baobab LIMS in the cloud.

**[DockerHub](https://hub.docker.com/) account needed.**

**Authentication: `admin:adminsecret`**

## Using [`Docker`](https://docs.docker.com/install/)

[![Docker Repository on Quay](https://quay.io/repository/baobab-lims/baobab-lims/status "Docker Repository on Quay")](https://quay.io/repository/baobab-lims/baobab-lims)

Kindly install docker using instructions from [here](https://www.docker.com/community-edition) and run the following command:

```sh
docker run -p 8080:8080 quay.io/baobab-lims/baobab-lims
```

## Using [`docker-compose`](https://docs.docker.com/install/):

```sh
$ pip install docker-compose
...
$ git clone https://github.com/BaobabLims/baobab.lims.git
$ cd baobab.lims
$ docker-compose up -d
```

**Access Baobab LIMS on [localhost:8080](http://localhost:8080):**

- Click on **`Install a Baobab distribution`**.
- Check **`Baobab LIMS`** option, then click **`Install`** the form.
- Authentication: **`admin:adminsecret`**

# Standalone Installation

Baobab LIMS Standalone [installation](https://github.com/hocinebendou/baobab.lims/wiki/Installation)

# Further Documentation

- [User Manual](https://b3abiobank.sanbi.ac.za/demo/manual.pdf)
- [Github Wiki](https://github.com/hocinebendou/baobab.lims/wiki)
- [Online Documentation](https://baobab-lims.readthedocs.io/en/latest/)
