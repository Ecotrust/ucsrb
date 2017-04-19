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
