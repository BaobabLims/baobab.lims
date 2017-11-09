==========
Installing
==========

Plone installation
==================

Here we describe how to install Plone onto the Ubuntu Linux System. For an installation in a different operating system, check the Plone online documentation, `here`_. The installation process requires users to have root priveledges and a basic knowledge of the Linux command lines using Terminal. If you are not familiar with a UNIX operating system, read this tutorial Linux shell `tutorial`_. Please note that a single line must be completed at a time. 

.. _here: http://docs.plone.org/4/en/manage/installing/installation.html
.. _tutorial: http://linuxcommand.org/learning_the_shell.php


Plone dependencies
------------------
 

``Plone`` framework requires the installation of additional system packages. Without these packages available in your system, Plone will not compile.

    ``$ sudo apt-get install build-essential gcc python-dev git-core libffi-dev``

    ``$ sudo apt-get install libpcre3 libpcre3-dev autoconf libtool pkg-config``

    ``$ sudo apt-get install zlib1g-dev libssl-dev libexpat1-dev libxslt1.1``

    ``$ sudo apt-get install gnuplot libcairo2 libpango1.0-0 libgdk-pixbuf2.0-0``


Download Plone 4.3 Unified Installer
------------------------------------

The Baobab LIMS is implemented and tested with Plone 4.3.11, a version released in 2016-09-12. You can download Plone 4.3.x by visiting the `Plone`_ site. Select and click on the Unified installer of your choice or use ``wget`` command line in your terminal with the path to the Plone version to install. Only Plone 4.3.11 can be used.

.. _Plone: https://plone.org/download


    ``$ wget --no-check-certificate https://launchpad.net/plone/4.3/4.3.11/+download/Plone-4.3.11-r1-UnifiedInstaller.tgz``

If the download has been done from the Plone site, the installer would be located in the  ``~/Downloads`` directory. If the second option used i.e, the wget command line, the installer should be downloaded into the current directory.

Install Ploner
-------------

To continue the installation, in the terminal, change directory to the folder containing the downloaded file then run the following command line to unpack the archive file.

    ``$ tar -xf Plone-4.3.11-r1-UnifiedInstaller.tgz``

Change to the extracted folder in the terminal.

    ``$ cd Plone-4.3.11-r1-UnifiedInstaller``

Run the following command to install Plone
    
    ``$ ./install.sh --target=/usr/local/Plone --build-python zeo``

    ``$ ./install.sh --target=/home/ubuntu/Plone --build-python zeo``

where ``--target`` parameter is used to specify the path to the installation folder, ``--build`` python will add and build Python package in your system, (this is optional if Python already exist) and finally zeo option will install Plone as a Client-Server application. Plone requires Python2.7 in order to operate. Run ./install.sh --help to obtain the full list of the available parameters and their meaning.

.. Note:: In production mode, prepend the previous command line with ``sudo`` and run.


Install Baobab LIMS
===================

In the new folder created ``/usr/local/Plone`` , another folder named zeocluster can be found. This folder contains the configuration file, buildout.cfg. Find in the configuration file, and in the section starting with eggs=, add bika.lims and baobab.lims  to the existing entries. 

.. Note:: Bika LIMS is a dependency that Baobab LIMS needs to function. Some of modules in Baobab LIMS reference modules in Bika LIMS.

   ``$ eggs =``

 		``Plone``

 		``Pillow``

 		``bika.lims``

 		``baobab.lims``

Add to the section developer = the path to your version of Baobab LIMS and BIKA LIMS that should be already downloaded into your local machine. By convention it is preferable to put the source code in zeocluster/src of your Plone installation folder.

Add to the section developer = the path to your version of Baobab LIMS and BIKA LIMS that should be already downloaded into your local machine. By convention it is preferable to put the source code in ``zeocluster/src`` of your Plone installation folder.

   ``$ developer =``

   		``src/baobab.lims``

   		``src/bika.lims``

Use git clone or fork this project to have your own copy in your local machine. For developers, any change in your source code that you judge interesting and useful for the community please create a ``Pull`` request and let us know if you want to become a collaborator in the Baobab LIMS project.

Links below;
`Bika labs`_
`Baobab LIMS`_

.. _Bika labs: https://github.com/bikalabs/bika.lims.git
.. _Baobab LIMS: https://github.com/BaobabLims/baobab.lims.git

Save the file, and run ``bin/buildout -n``. Buildout will download and install all the declared dependencies.

If you installed ``Plone`` as a root user i.e., using sudo, you should run the buildout command line with the user plone_buildout, this user is automatically created during the Plone installation:

    ``$ sudo -u plone_buildout bin/buildout``

.. warning::
    If you encounter the ``packages not found`` issue, add the following line, 
    issue related to this: https://github.com/BaobabLims/baobab.lims/issues/55
    
    ``index = https://pypi.python.org/simple/``
    
    Add the above line in the ``[buildout]`` section.

Test your installation
======================

First, you will need to start the zeoserver (this is the database process).

    ``$ bin/zeoserver start``

To start a Plone client in debug mode, run this command:

    ``$ bin/client1 fg``

If you installed Plone as a root user, you will need to use the following commands instead:

    ``$ sudo -u plone_daemon bin/zeoserver start``

    ``$ sudo -u plone_daemon bin/client1 fg``

.. Note:: any error messages, and take corrective action if required. If no errors are encountered, you can press Control+C to exit.

In your preferred browser, Firefox or google chrome, run `http://localhost:8080/'_ and start working with Baobab LIMS. Enjoy it!

If installed on a remote server, an IP address (of the server) is associated with the use of LIMS eg: https://192.168.1.1:8080/

In production mode, other important tools need to be installed and configured, like ``Supervisorctl`` and nginx. The following `article`_ details the process to follow to add those tools cited before.


.. _http://localhost8080/: http://localhost:8080/
.. _article: http://docs.plone.org/manage/deploying/production/ubuntu_production.html


 
