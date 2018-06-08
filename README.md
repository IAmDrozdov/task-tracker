![](https://cdn1.savepice.ru/uploads/2018/6/8/356b8ce2066e0af12499c56adf2cb590-full.png)             
![Python](https://img.shields.io/badge/python-v3.6-blue.svg)
![Dependencies](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen.svg)
![Contributions welcome](https://img.shields.io/badge/contributions-welcome-orange.svg)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)

# Welcome
This project consist of library from which you can develop your own to-do application.
Also there is example of cli and web interfaces for this library.
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
