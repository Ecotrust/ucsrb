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
python manage.py enable_sharing --all
python manage.py runserver 0.0.0.0:8000
```
Then go [here](http://localhost:8111/visualize)

### ~Production Installation

#### Bootstrap [MarinePlanner](https://github.com/Ecotrust/marineplanner-core/blob/master/README.md#stageproduction-installation-ubuntu-lts)

#### Clone UCSRB and Components
```bash
cd /usr/local/apps/marineplanner-core/apps
git clone https://github.com/Ecotrust/ucsrb.git
cd ucsrb/scripts
chmod +x configure_project.sh
cp configure_project.sh /usr/local/apps/marineplanner-core/scripts/configure_project.sh
cd /usr/local/apps/marineplanner-core/scripts/
./configure_project.sh ucsrb
cd /usr/local/apps/marineplanner-core/apps/ucsrb/ucsrb/
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

#### NEW: Install dhsvm_harness
```
cd /usr/local/apps/marineplanner-core/apps
git clone https://github.com/Ecotrust/uc-dhsvm-harness.git
pip install -e /usr/local/apps/marineplanner-core/apps/uc-dhsvm-harness
```

#### NEW: Install Celery and Broker
```
sudo apt install redis-server -y
sudo vim /etc/redis/redis.conf
```

Update the `supervised` setting to read: `supervised systemd`

```
sudo systemctl restart redis.service
pip install redis
pip install "celery<5.0"
pip install "django-celery-results<2.2"

ln -s /usr/local/apps/marineplanner-core/apps/ucsrb/ucsrb/celery.py /usr/local/apps/marineplanner-core/marineplanner/marineplanner/celery.py
cat /usr/local/apps/marineplanner-core/apps/ucsrb/ucsrb/__init__.py >> /usr/local/apps/marineplanner-core/marineplanner/marineplanner/__init__.py
```

Adding celery user -- be sure to come up with a good password and keep it safe.
```
sudo adduser celery
sudo mkdir /var/log/celery
sudo chown celery:celery /var/log/celery
sudo mkdir /var/run/celery
sudo chown celery:celery /var/run/celery
sudo mkdir /etc/conf.d
```
celery settings:
```
sudo cp /usr/local/apps/marineplanner-core/apps/ucsrb/deployment/celery.conf /usr/lib/tmpfiles.d/celery.conf
sudo cp /usr/local/apps/marineplanner-core/apps/ucsrb/deployment/celery.service /etc/systemd/system/celery.service
sudo cp /usr/local/apps/marineplanner-core/apps/ucsrb/deployment/celery /etc/conf.d/celery

sudo mkdir /var/log/celery/
sudo chmod 755 /var/log/celery/
sudo chown celery:celery /var/log/celery/

sudo mkdir /var/run/celery/
sudo chmod 755 /var/run/celery/
sudo chown celery:celery /var/run/celery/

sudo systemctl enable celery.service
sudo systemctl daemon-reload
sudo systemctl start celery.service
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

upload them to the data folder you just created

#### Wrap up the tool installation

```
cd /usr/local/apps/marineplanner-core/marineplanner
python manage.py migrate
python manage.py collectstatic
````

#### Import your data

```
python manage.py import_veg_units /usr/local/apps/marineplanner-core/data/__YOUR_VEG_FILE___

# import_focus_areas <path to data> <data category HUC10, HUC12, or RMU>
python manage.py import_focus_areas /usr/local/apps/marineplanner-core/data/__YOUR_HUC_10_FILE__ HUC10
python manage.py import_focus_areas /usr/local/apps/marineplanner-core/data/__YOUR_HUC_12_FILE__ HUC12
python manage.py import_focus_areas /usr/local/apps/marineplanner-core/data/__YOUR_RMU_FILE RMU
python manage.py import_pourpoints /usr/local/apps/marineplanner-core/data/__YOUR_POUR_POINT_BASIN_FILE__
python manage.py import_climate_data /usr/local/apps/marineplanner-core/data/__YOUR_CLIMATE_DATA_FILE__
```

```
python manage.py createsuperuser
```

* `enter` to use default option, or enter your own email
* add a password for your superuser


```
python manage.py enable_sharing --all

```

#### Generate baseline flow data:
Run each of the following commands, some may take several hours:
```
python manage.py set_baseline_flow Entiat
python manage.py set_baseline_flow Methow
python manage.py set_baseline_flow Okanogan
python manage.py set_baseline_flow Wenatchee
```

#### Enable Anonymous User
Use your admin user to create an anonymous user (this assumes port 8000 is open)
```
python manage.py runserver 0:8000
```
Navigate to your site's port 8000 and log in to your sites `/admin/` page.
Create a new user (let's call her 'Anonymous').
Note the ID created for the user
* this can be found in the URL which might look something like `/adminauth/user/2/change/`
   * The `2` would be the id in this case (it will be numeric)

Update your local settings with something like:
```
ALLOW_ANONYMOUS_DRAW = True
ANONYMOUS_USER_PK = 2
```

#### Install and Configure NGINX and UWSGI

```
sudo apt-get install nginx uwsgi uwsgi-plugin-python3 -y
pip install uwsgi

sudo cp /usr/local/apps/marineplanner-core/apps/ucsrb/deployment/marineplanner_nginx.conf /etc/nginx/sites-available/marineplanner
sudo rm /etc/nginx/sites-enabled/default
sudo ln -s /etc/nginx/sites-available/marineplanner /etc/nginx/sites-enabled/marineplanner
sudo cp /usr/local/apps/marineplanner-core/deployment/uwsgi_params /etc/nginx/

sudo cp /usr/local/apps/marineplanner-core/deployment/emperor.ini /etc/uwsgi/
sudo ln -s /usr/local/apps/marineplanner-core/deployment/uwsgi.service /etc/systemd/system/
sudo ln -s /usr/local/apps/marineplanner-core/apps/ucsrb/deployment/marineplanner.ini /etc/uwsgi/apps-enabled/

sudo chmod +x /usr/local/apps/marineplanner-core/deployment/restart_nginx.sh

sudo service uwsgi start
sudo service uwsgi restart
sudo cp /usr/local/apps/marineplanner-core/deployment/rc.local /etc/rc.local
```

#### Install and Configure Email
`sudo apt-get install postfix `
configuration:  
     Internet Site
System mail name :
     enter the domain name you plan to use, i.e.: s2f.ucsrb.org

Then set Django settings to look something like this:
```
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False
DEFAULT_FROM_EMAIL = 'MarinePlanner<marineplanner@your.domain>'
```
Configure DNS for secure delivery (see internal documentation)

#### Configure ReCaptcha and Registration
**NOTE: This does not seem required for the signup popup, only if user finds /account/**
* pip install django-recaptcha
* Install with [these directions]https://github.com/praekelt/django-recaptcha#installation
* Use the 'NOCAPTCHA' setting (True)

#### Install and Configure Munin
```
sudo apt-get install munin munin-node
sudo vim /etc/nginx/sites-enabled/marineplanner
```

Between the `error_log` line and the `location /static ` line add:
```
location /munin/static/ {
        alias /etc/munin/static/;
}

location /munin {
        alias /var/cache/munin/www;
}
```

Then restart NGINX

```
sudo service nginx restart
```

#### Automatic (Unattended) Security Updates
From the document [Using the "unattended-upgrades" package](https://help.ubuntu.com/community/AutomaticSecurityUpdates#Using_the_.22unattended-upgrades.22_package)

Install the unattended-upgrades package if it isn't already installed:
```
sudo apt-get install unattended-upgrades
```

To enable it, do:
```
sudo dpkg-reconfigure --priority=low unattended-upgrades
```
(it's an interactive dialog) which will create `/etc/apt/apt.conf.d/20auto-upgrades` with the following contents:
```
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
```
To have the server automatically reboot when necessary to install security upddates:
1. install the package `update-notifier-common`
```
sudo apt-get install update-notifier-common
```
1. edit the file `/etc/apt/apt.conf.d/50unattended-upgrades` near the bottom you will find the line
```
//Unattended-Upgrade::Automatic-Reboot "false";
```
uncomment it and set value to true:
```
Unattended-Upgrade::Automatic-Reboot "true";
```
To tell the server what time is most safe to reboot (when needed), uncomment the line
```
//Unattended-Upgrade::Automatic-Reboot-Time "02:00";
```
And set the time to your desired restart time.

Read the source document for more details.
