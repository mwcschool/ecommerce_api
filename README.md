# ecommerce API

## Setup
Before you start, it's recommended to create a new virtualenv for the application
### Linux Ubuntu
```
mkvirtualenv ecommerce -p /usr/bin/python3
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

## Heroku Support
From terminal, navigate to the root directory of your application
Install Heroku command line tool and launch the following command
```
heroku create
```
Push the content of your repository on Heroku
```
git push heroku name_of_your_branch:master
```
Create a .env file with the following environment variables
```
PYTHONPATH=.
FLASK_APP=app.py
FLASK_DEBUG=1
ENVIRONMENT=dev
```
Install PostgreSQL addon on Heroku with the command
```
heroku addons:create heroku-postgresql:hobby-dev
```
Set a config var for Heroku server with the command
```
heroku config:set ENVIRONMENT=production
```

## Demo scripts
These scripts create fake contents in the database for local testing purpose.

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
