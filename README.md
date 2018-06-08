&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
![](https://cdn1.savepice.ru/uploads/2018/6/8/356b8ce2066e0af12499c56adf2cb590-full.png)             
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
![Python](https://img.shields.io/badge/python-v3.6-blue.svg)
![Dependencies](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen.svg)
![Contributions welcome](https://img.shields.io/badge/contributions-welcome-orange.svg)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

# Welcome
This project consist of library from which you can develop your own to-do application.
Also there is example of cli and web interfaces for this library.

## Features
* 2 types of creating tasks.
* The ability to set the time remind.
* Sharing tasks between users.
* Set default database.

## Getting Started

### Prerequisites
This library require:
* `pip==3`, if not `sudo apt-get install -y python3-pip`
* `django==1.11`, if not: `pip3 install Django==1.11`
* `psycopg2-binary==2.8`, if not : `pip3 install psycopg2-binary`

### Installing 
* Download:

`git clone https://sashasashadrozdov@bitbucket.org/sashasashadrozdov/calendoola.git`

* Go to **library** repository and install:

`python3 setup.py install --user`

Library automatically create postgres user **calendoola** with password **1111** and database **calendoola_db** and run migrations.
You can user your own `settings.py` file, for this change default pass in 'configure.py' and run migrations.


## Code examples
```python
import calelib
calelib.configure_database()

from calelib.crud import Calendoola
calendoola_instance = Calendoola()
calendoola_instance.create_user('test_user')
```
To see all functions use `help(calelib)`.

## Tests 
To run tests go to tests folder and run `python3 -m unittests test*`.

## Contributors
When contributing to this repository, please first discuss the change you wish to make via issue, email, or any other method with the owners of this repository before making a change.

Please note we have a code of conduct, please follow it in all your interactions with the project.

## Authors
* Alexander Drozdov - **BSUIR**

## License
Distributed under the MIT license. See [LICENSE](LICENSE) for more information.