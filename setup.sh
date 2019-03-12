cd frontend
npm install

npm run dev

npm run build

cd ../backend
virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt