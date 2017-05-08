# ecommerce API

## Setup

Before you start, you must create a new virtualenv for the application
### Linux Ubuntu
```
mkvirtualenv -p python3 ecommerce
```
### macOS
```
virtualenv ecommerce
source ecommerce/bin/activate
```
Then, install required modules with command
```
pip3 install -r requirements.txt
```

## Demo scripts

These scripts create fake content in database for testing purpose.

`init-db.py` initialize database by deleting existing tables and creating new ones.
`demo-content.py` inserts random contents in database tables created by init-db.py.

You must first run init-db.py before to launch demo-content.py.
Enter in the virtualenv and run scripts by command line:
```
PYTHONPATH=. python scripts/init-db.py
```

After initialization of database, run:
```
PYTHONPATH=. python scripts/demo-content.py
```
