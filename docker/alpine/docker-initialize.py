#!/usr/local/bin/python

import re
import os

class Environment(object):
    """ Configure container via environment variables
    """
    def __init__(self, env=os.environ,
                 zope_conf="/plone/instance/parts/instance/etc/zope.conf",
                 custom_conf="/plone/instance/custom.cfg",
                 zeopack_conf="/plone/instance/bin/zeopack",
                 zeoserver_conf="/plone/instance/parts/zeoserver/etc/zeo.conf",
                 cors_conf="/plone/instance/parts/instance/etc/package-includes/999-additional-overrides.zcml"
                 ):
        self.env = env
        self.zope_conf = zope_conf
        self.custom_conf = custom_conf
        self.zeopack_conf = zeopack_conf
        self.zeoserver_conf = zeoserver_conf
        self.cors_conf = cors_conf

    def zeoclient(self):
        """ ZEO Client
        """
        server = self.env.get("ZEO_ADDRESS", None)
        if not server:
            return

        config = ""
        with open(self.zope_conf, "r") as cfile:
            config = cfile.read()

        # Already initialized
        if "<blobstorage>" not in config:
            return

        read_only = self.env.get("ZEO_READ_ONLY", "false")
        zeo_ro_fallback = self.env.get("ZEO_CLIENT_READ_ONLY_FALLBACK", "false")
        shared_blob_dir=self.env.get("ZEO_SHARED_BLOB_DIR", "off")
        zeo_storage=self.env.get("ZEO_STORAGE", "1")
        zeo_client_cache_size=self.env.get("ZEO_CLIENT_CACHE_SIZE", "128MB")
        zeo_conf = ZEO_TEMPLATE.format(
            zeo_address=server,
            read_only=read_only,
            zeo_client_read_only_fallback=zeo_ro_fallback,
            shared_blob_dir=shared_blob_dir,
            zeo_storage=zeo_storage,
            zeo_client_cache_size=zeo_client_cache_size
        )

        pattern = re.compile(r"<blobstorage>.+</blobstorage>", re.DOTALL)
        config = re.sub(pattern, zeo_conf, config)

        with open(self.zope_conf, "w") as cfile:
            cfile.write(config)

    def zeopack(self):
        """ ZEO Pack
        """
        server = self.env.get("ZEO_ADDRESS", None)
        if not server:
            return

        if ":" in server:
            host, port = server.split(":")
        else:
            host, port = (server, "8100")

        with open(self.zeopack_conf, 'r') as cfile:
            text = cfile.read()
            text = text.replace('address = "8100"', 'address = "%s"' % server)
            text = text.replace('host = "127.0.0.1"', 'host = "%s"' % host)
            text = text.replace('port = "8100"', 'port = "%s"' % port)

        with open(self.zeopack_conf, 'w') as cfile:
            cfile.write(text)

    def zeoserver(self):
        """ ZEO Server
        """
        pack_keep_old = self.env.get("ZEO_PACK_KEEP_OLD", '')
        if pack_keep_old.lower() in ("false", "no", "0", "n", "f"):
            with open(self.zeoserver_conf, 'r') as cfile:
                text = cfile.read()
                if 'pack-keep-old' not in text:
                    text = text.replace(
                        '</filestorage>',
                        '  pack-keep-old false\n</filestorage>'
                    )

            with open(self.zeoserver_conf, 'w') as cfile:
                cfile.write(text)

    def cors(self):
        """ Configure CORS Policies
        """
        if not [e for e in self.env if e.startswith("CORS_")]:
            return

        allow_origin = self.env.get("CORS_ALLOW_ORIGIN",
            "http://localhost:3000,http://127.0.0.1:3000")
        allow_methods = self.env.get("CORS_ALLOW_METHODS",
            "DELETE,GET,OPTIONS,PATCH,POST,PUT")
        allow_credentials = self.env.get("CORS_ALLOW_CREDENTIALS", "true")
        expose_headers = self.env.get("CORS_EXPOSE_HEADERS",
            "Content-Length,X-My-Header")
        allow_headers = self.env.get("CORS_ALLOW_HEADERS",
            "Accept,Authorization,Content-Type,X-Custom-Header,Lock-Token")
        max_age = self.env.get("CORS_MAX_AGE", "3600")
        cors_conf = CORS_TEMPLATE.format(
            allow_origin=allow_origin,
            allow_methods=allow_methods,
            allow_credentials=allow_credentials,
            expose_headers=expose_headers,
            allow_headers=allow_headers,
            max_age=max_age
        )
        with open(self.cors_conf, "w") as cfile:
            cfile.write(cors_conf)

    def buildout(self):
        """ Buildout from environment variables
        """
        # Already configured
        if os.path.exists(self.custom_conf):
            return

        findlinks = self.env.get("FIND_LINKS", "").strip().split()

        eggs = self.env.get("PLONE_ADDONS",
               self.env.get("ADDONS", "")).strip().split()

        zcml = self.env.get("PLONE_ZCML",
               self.env.get("ZCML", "")).strip().split()

        develop = self.env.get("PLONE_DEVELOP",
                  self.env.get("DEVELOP", "")).strip().split()

        site = self.env.get("PLONE_SITE",
               self.env.get("SITE", "")).strip()

        profiles = self.env.get("PLONE_PROFILES",
                   self.env.get("PROFILES", "")).strip().split()

        versions = self.env.get("PLONE_VERSIONS",
                   self.env.get("VERSIONS", "")).strip().split()

        sources = self.env.get("SOURCES", "").strip()
        sources = sources and [x.strip() for x in sources.split(",")]

        buildout_extends = ((develop or sources)
                            and "develop.cfg" or "buildout.cfg")

        buildout_extends = ((develop or sources)
                            and ["develop.cfg"] or ["buildout.cfg"])
        extra_extends = self.env.get("BUILDOUT_EXTENDS", "").strip().split()
        buildout_extends.extend(extra_extends)

        # If profiles not provided. Install ADDONS :default profiles
        if not profiles:
            for egg in eggs:
                base = egg.split("=")[0]
                profiles.append("%s:default" % base)

        enabled = bool(site)
        if not (eggs or zcml or develop or enabled or extra_extends):
            return

        buildout = BUILDOUT_TEMPLATE.format(
            buildout_extends="\n\t".join(buildout_extends),
            findlinks="\n\t".join(findlinks),
            eggs="\n\t".join(eggs),
            zcml="\n\t".join(zcml),
            develop="\n\t".join(develop),
            profiles="\n\t".join(profiles),
            versions="\n".join(versions),
            site=site or "Plone",
            enabled=enabled,
        )

        # If we need to create a plonesite and we have a zeo setup
        # configure collective.recipe.plonesite properly
        server = self.env.get("ZEO_ADDRESS", None)
        if server:
            buildout += ZEO_INSTANCE_TEMPLATE.format(zeoaddress=server)

        # Add sources configuration if needed
        if sources:
            buildout += SOURCES_TEMPLATE.format(sources="\n".join(sources))

        with open(self.custom_conf, 'w') as cfile:
            cfile.write(buildout)

    def setup(self, **kwargs):
        self.buildout()
        self.cors()
        self.zeoclient()
        self.zeopack()
        self.zeoserver()

    __call__ = setup

ZEO_TEMPLATE = """
    <zeoclient>
      read-only {read_only}
      read-only-fallback {zeo_client_read_only_fallback}
      blob-dir /data/blobstorage
      shared-blob-dir {shared_blob_dir}
      server {zeo_address}
      storage {zeo_storage}
      name zeostorage
      var /plone/instance/parts/instance/var
      cache-size {zeo_client_cache_size}
    </zeoclient>
""".strip()

CORS_TEMPLATE = """<configure
  xmlns="http://namespaces.zope.org/zope">
  <configure
    xmlns="http://namespaces.zope.org/zope"
    xmlns:plone="http://namespaces.plone.org/plone">
    <plone:CORSPolicy
      allow_origin="{allow_origin}"
      allow_methods="{allow_methods}"
      allow_credentials="{allow_credentials}"
      expose_headers="{expose_headers}"
      allow_headers="{allow_headers}"
      max_age="{max_age}"
     />
  </configure>
</configure>
"""

BUILDOUT_TEMPLATE = """
[buildout]
extends = {buildout_extends}
find-links += {findlinks}
develop += {develop}
eggs += {eggs}
zcml += {zcml}

[plonesite]
enabled = {enabled}
site-id = {site}
profiles += {profiles}

[versions]
{versions}
"""

ZEO_INSTANCE_TEMPLATE = """

[instance]
zeo-client = true
zeo-address = {zeoaddress}
shared-blob = off
http-fast-listen = off
"""

SOURCES_TEMPLATE = """

[sources]
{sources}
"""


def initialize():
    """ Configure Plone instance as ZEO Client
    """
    environment = Environment()
    environment.setup()

if __name__ == "__main__":
    initialize()