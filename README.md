# Loan Defaulter Risk Checker — Railway Deploy

A Flask web app to assess loan default risk based on financial profile.

## Project Structure

```
loan_defaulter_app/
├── app.py               ← Flask backend (API + server)
├── templates/
│   └── index.html       ← Frontend UI
├── requirements.txt     ← Python dependencies
├── Procfile             ← Railway/Heroku start command
├── railway.json         ← Railway config
├── loan_checker.py      ← Standalone Python console app
└── README.md
```

---

## Deploy on Railway (Step by Step)

### Step 1 — Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/loan-defaulter-app.git
git push -u origin main
```

### Step 2 — Deploy on Railway
1. Go to https://railway.app and sign in
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway auto-detects Python and deploys using Procfile
5. Click "Generate Domain" under Settings → Networking
6. Your app will be live at https://your-app-name.up.railway.app

### Step 3 — Environment Variables
Railway auto-sets PORT. No extra env vars needed.

---

## Run Locally

```bash
pip install -r requirements.txt
python app.py
# Visit http://localhost:5000
```
