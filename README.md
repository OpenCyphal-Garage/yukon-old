# Installation & Development Instructions

``` bash

# install frontend
cd frontend
npm install

# serve with hot reload at localhost:8080
npm run dev

# build for production/Flask with minification
npm run build

# install backend
cd ../backend
virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt

# serve /backend/run.py at localhost:5000
FLASK_APP=run.py flask run
```

## Or run setup.sh

(You have to run flask manually after)