# ucsrb

Core Django module for UCSRB Tool on MarinePlanner stack.

### ~Development Installation

#### Bootstrap [MarinePlanner](https://github.com/Ecotrust/marineplanner-core):

###### MAC
If you have [Vagrant](https://www.vagrantup.com/downloads.html) installed on Mac:
```bash
git clone https://github.com/Ecotrust/marineplanner-core.git
cd marineplanner-core/scripts
cp configure_project.sh.template.mac configure_project.sh
chmod +x configure_project.sh
./configure_project.sh ucsrb
vagrant up
```

###### Linux
If you have [Vagrant](https://www.vagrantup.com/downloads.html) installed on Linux:
```bash
git clone https://github.com/Ecotrust/marineplanner-core.git
cd marineplanner-core/scripts
cp configure_project.sh.template configure_project.sh
chmod +x configure_project.sh
./configure_project.sh ucsrb
vagrant up
```

###### Run test server
```bash
vagrant ssh
djrun
```
...Or if that doesn't work:
```bash
vagrant ssh
cd /usr/local/apps/marineplanner-core/
source env/bin/activate
cd marineplanner
python manage.py runserver 0.0.0.0:8000
```
Then go [here](http://localhost:8111/visualize)

### ~Production Installation

#### Bootstrap [MarinePlanner](httpshttps://github.com/Ecotrust/marineplanner-core/blob/master/README.md#stageproduction-installation-ubuntu-lts)

#### Clone UCSRB and Components
```bash
cd /usr/local/apps/marineplanner-core/apps
git clone https://github.com/Ecotrust/ucsrb.git
cd ucsrb/scripts
chmod +x configure_project.sh
cp configure_project.sh /usr/local/apps/marineplanner-core/scripts/configure_project.sh
cd /usr/local/apps/marineplanner-core/scripts/
./configure_project.sh ucsrb
cd /usr/local/apps/marineplanner-core/apps/ucsrb/
./vagrant_provision.sh marineplanner-core marineplanner marineplanner /usr/local/apps/marineplanner-core/apps/ucsrb/ucsrb
/usr/local/apps/marineplanner-core/apps/mp-accounts/scripts/vagrant_provision.sh marineplanner-core
/usr/local/apps/marineplanner-core/apps/mp-visualize/scripts/vagrant_provision.sh marineplanner-core
/usr/local/apps/marineplanner-core/apps/madrona-scenarios/scripts/vagrant_provision.sh marineplanner-core
/usr/local/apps/marineplanner-core/scripts/vagrant_finish_provision.sh marineplanner-core marineplanner
```

NOTE: Currently a few modules do not seem to be cloned and added automatically (mp-drawing, madrona-analysistools, etc...)
* clone these into apps/
* run `pip install -e /usr/local/apps/marineplanner-core/apps/______` for each to install it (replace the ______ )
* run `pip install -r ______/requirements.txt` if a requirements.txt resides under a new repo's parent dir.

```
cd /usr/local/apps/marineplanner-core/apps/ucsrb/ucsrb/
cp local_settings.py.template local_settings.py
vim local_settings.py
```

#### Set your local settings:
* Add your mapbox access token tp `MAPBOX_ACCESS_TOKEN`
* `COMPRESS_ENABLED = False` (for now)
* `ALLOW_ANONYMOUS_DRAW = False` (for now)
* `ANONYMOUS_USER_PK = 2` (for now)
* `USE_TZ = False` (this should really be in settings.py)
* Set `ALLOWED_HOSTS` = to `[ '_____']` replacing the blank with your url or IP address

#### Load your data
On your server, create the directory `/usr/local/apps/marineplanner-core/data`
From your workstation, locate input files for the following:
* HUC 10s
* HUC 12s
* RMUs
* Pour Point Basins
* Veg Units
* climate data

upload them to the data file you just created

#### Wrap up the tool installation

```
cd /usr/local/apps/marineplanner-core/marineplanner
python manage.py migrate
python manage.py collectstatic

python manage.py import_veg_units /usr/local/apps/marineplanner-core/data/__YOUR_VEG_FILE___
python manage.py import_focus_areas HUC10 /usr/local/apps/marineplanner-core/data/__YOUR_HUC_10_FILE__
python manage.py import_focus_areas HUC12 /usr/local/apps/marineplanner-core/data/__YOUR_HUC_12_FILE__
python manage.py import_focus_area RMU /usr/local/apps/marineplanner-core/data/__YOUR_RMU_FILE
python manage.py import_pourpoints /usr/local/apps/marineplanner-core/data/__YOUR_POUR_POINT_BASIN_FILE__
python manage.py {CLIMATE DATA COMING SOON! ~RDH}

python manage.py createsuperuser

```

### Install and Configure NGINX, UWSGI, and Munin
