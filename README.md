# Baobab LIMS

Baobab LIMS is an open-source laboratory information management system (LIMS) software that will ensure that researchers can track the lifecycle of a biospecimen in the laboratory from receipt to storage and reuse. This software ensures that sufficient metadata is captured.

_Baobab_ is a common name given to nine tree species in different countries in the world, mostly in Africa.

Baobab LIMS written in Plone, a python framework known for its robustness, and inherits some modules from Bika LIMS.

## Try it out

### Using PWD

Click the _Try in PWD_ button below to get 4 hours to try Baobab LIMS in the cloud.

**[DockerHub](https://hub.docker.com/) account needed.**

**Use `admin:adminsecret` for `username:password`.**

[![Try in PWD](https://cdn.rawgit.com/play-with-docker/stacks/cff22438/assets/images/button.png)](http://play-with-docker.com?stack=https://raw.githubusercontent.com/BaobabLims/baobab.lims/master/stack.yml)

### Using our [`docker`](https://docs.docker.com/install/) container:

[![Docker Repository on Quay](https://quay.io/repository/baobab-lims/baobab-lims/status "Docker Repository on Quay")](https://quay.io/repository/baobab-lims/baobab-lims)

Kindly install docker using instructions from [here](https://www.docker.com/community-edition) and run the following command:

```sh
docker run -p 8080:8080 quay.io/baobab-lims/baobab-lims
```

**Access Baobab LIMS on [localhost:8080](http://localhost:8080):**

- Click on `Install a Baobab distribution`.
- Check `Baobab LIMS` option, then click `Install` the form.
- Authentication: `admin:adminsecret`

### Using [`docker-compose`](https://docs.docker.com/install/):

- Baobab LIMS `docker-compose` [installation](https://github.com/BaobabLims/baobab.lims/blob/master/docker/README.md)

## Standalone installation:

- Baobab LIMS Standalone [installation](https://github.com/hocinebendou/baobab.lims/wiki/Installation)

## Documentation

- [User Manual](https://b3abiobank.sanbi.ac.za/demo/manual.pdf)
- [Github Wiki](https://github.com/hocinebendou/baobab.lims/wiki)

## Feedback and Support

- Baobab LIMS Team on [Gitter](https://gitter.im/BaobabLims/Lobby)
- Issues can be submitted via [GitHub Issues](https://github.com/BaobabLims/baobab.lims/issues)
