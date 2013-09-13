# WholeCellDB v1.1.0
1. [About](#about)
2. [Requirements](#requirements)
   1. [Mimimum requirements](#requirements_minimum)
   2. [Additional requirments for production servers](#requirements_production)
3. [Getting started](#starting)
4. [Integrating WholeCellDB with Whole-cell models](#integrating)
5. [Need help?](#help)
6. [Implementation](#implementation)
7. [Development team](#team)
8. [License](#license)


<a name="about"/>
## About
WholeCellDB is a hybrid SQL/HDF database for storing and retrieving whole-cell model predictions. WholeCellDB is implemented in Python using the Django framework.

See [wholecell.stanford.edu](http://wholecell.stanford.edu) for additional information about whole-cell models.

<a name="requirements"/>
## Requirements

<a name="requirements_minimum"/>
### Mimimum requirements
* python 2.7
* Django 1.5
* hdf5
* hdf5-devel
* python-numpy
* python-h5py

<a name="requirements_production"/>
### Additional requirments for production servers
* apache
* mod_wsgi

<a name="starting"/>
## Getting started

1. Setup your database in the `DATABASES` dict in `WholeCellDB/settings.py`. For more information on how you can do this, see the [django tutorial](https://docs.djangoproject.com/en/1.5/intro/tutorial01/#database-setup).
    * To use SQLite set the `ENGINE` property to `django.db.backends.sqlite3` and set the `NAME` property to the path to the database file
    * To use MySQL (1) create a new user and database and (2) set the `ENGINE` property to `django.db.backends.mysql` and set the `HOST`, `PORT`, `NAME`, `USER`, and `PASSWORD` properties
2. In the `wcdb/models.py` file, change the value of `HDF5_ROOT` to the location you wish to save the HDF5 data.

        HDF5 = "/path/to/my/hdf5/location"
3. Run `python manage.py syncdb` to create the models. 
4. Configure your web server
    * Run `python manage.py runserver` to start the development server, or
    * Add the following to your Apache configuration (`/etc/httpd/conf.d/WholeCellDB.conf and restart
5. Navigate to the WholeCellDB website using your webserver
    * Development server: [http://localhost:8000](http://localhost:8000)
    * Production server:

            LoadModule wsgi_module modules/mod_wsgi.so
            
            WSGIDaemonProcess default processes=2 threads=25
            WSGIDaemonProcess wholecelldb:1 threads=1
            WSGIDaemonProcess wholecelldb:2 threads=1
            WSGIDaemonProcess wholecellkbeco:1 threads=25
            SetEnv PROCESS_GROUP default
            WSGIProcessGroup %{ENV:PROCESS_GROUP}
            WSGISocketPrefix /var/run/wsgi
            
            #Alias /projects/WholeCellDB/static /home/projects/WholeCell-Mpn/kb/static
            Alias /projects/WholeCellDB /home/projects/WholeCellDB/WholeCellDB/wsgi.py
            <Directory /home/projects/WholeCellDB/WholeCellDB>
                WSGIApplicationGroup %{RESOURCE}
                WSGIRestrictProcess wholecelldb:1 wholecelldb:2
                SetEnv PROCESS_GROUP wholecelldb:1
                AddHandler wsgi-script .py
                Options ExecCGI
                Order allow,deny
                Allow from all
            </Directory>

<a name="integrating"/>
## Integrating WholeCellDB with whole-cell models
Use the following code to import the WholeCellDB packages into Python:

    import sys

    # Add the project to your path.
    sys.path.append('/path/to/WholeCellDB/project')

    # Setup the environment using the projects settings.
    from WholeCellDB import settings
    from django.core.management import setup_environ
    setup_environ(settings)

    # Import the models
    from wcdb.models import Simulation, Property
    
<a name="help"/>
## Need help?
Please contact the development team at [insert@email.address](mailto:insert@email.address).

<a name="implementation"/>
## Implementation
*Briefly describe implementation.*

<a name="team"/>
## Development team
WholeCellDB was developed by researchers at the University of Prince Edward Island and Stanford University.

* [Nolan Phillips](http://ca.linkedin.com/pub/nolan-phillips/68/935/702), University of Prince Edward Island
* [Jonathan Karr](http://www.stanford.edu/~jkarr), Stanford University
* [Markus Covert](http://covertlab.stanford.edu), Stanford University
* [Yingwei Wang](http://www.csit.upei.ca/~ywang/), University of Prince Edward Island

<a name="license"/>
## License
*Add a license here. We usually use the MIT license.*
