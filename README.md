# ecommerce API

## Setup
Before you start, it's recommended to create a new virtualenv for the application
### Linux Ubuntu
```
mkvirtualenv -p python3 ecommerce
```

### macOS
```
virtualenv -p python3 ecommerce
source ecommerce/bin/activate
```

Then, install the required modules with the command
```
pip3 install -r requirements.txt
```

## Demo scripts
These scripts create fake contents in the database for testing purpose.

`init-db.py` initialize the database by deleting existing tables and creating new ones.
`demo-content.py` inserts random contents in database tables created by `init-db.py`.

You must first run `init-db.py` before launch `demo-content.py`.
Enter in the virtualenv and run scripts by command line:
```
PYTHONPATH=. python scripts/init-db.py
```

After initialization of database, run:
```
PYTHONPATH=. python scripts/demo-content.py
```
