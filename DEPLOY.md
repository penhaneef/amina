# Deploy Amina — step by step

## 0. What “access” means (important)

You do **not** give the AI your GitHub password.

| Safe | Unsafe |
|------|--------|
| You sign in to GitHub in **your browser** or **GitHub Desktop** | Sending password / tokens in chat |
| Install Git/GitHub Desktop on **this PC** so commands run as **you** | Sharing personal access tokens in plain chat |
| Create a public/private repo yourself, or approve `gh auth login` in the terminal | “Log in as me” via password |

Once Git is installed and you are logged in on this machine, the assistant can run `git` / `gh` commands **in your project folder** using your local login.

---

## 1. Install tools (one time)

### Option A — GitHub Desktop (easiest)

1. Download: https://desktop.github.com/
2. Install and sign in with your GitHub account (browser popup).
3. Continue with **section 2A**.

### Option B — Git + browser

1. Download Git: https://git-scm.com/download/win  
2. Install with defaults.
3. Open a **new** PowerShell window after install.
4. Continue with **section 2B**.

---

## 2. Put Amina on GitHub

### 2A — GitHub Desktop

1. **File → Add local repository** → choose `C:\Users\Aliyu\Desktop\Amina`  
   - If it says “not a git repository”, click **create a repository** here.
2. Confirm `.gitignore` is present (it should ignore `__pycache__`, venv, etc.).
3. Commit message: `Initial Amina app for Streamlit deploy`
4. **Publish repository**
   - Name: `amina` (or similar)
   - Keep private or public (your choice)
   - Publish

### 2B — Command line (after Git is installed)

```powershell
cd C:\Users\Aliyu\Desktop\Amina
git init
git add .
git status
git commit -m "Initial Amina app for Streamlit deploy"
```

Create an empty repo on https://github.com/new named `amina` (no README if you already have one locally), then:

```powershell
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/amina.git
git push -u origin main
```

(Browser will ask you to log in if needed.)

---

## 3. Streamlit Community Cloud

1. Open https://share.streamlit.io  
2. **Sign in with GitHub** and authorize Streamlit.  
3. **New app**  
   - Repository: `YOUR_USERNAME/amina`  
   - Branch: `main`  
   - Main file path: **`app.py`**  
4. **Deploy**  
5. Wait for the URL (e.g. `https://amina-xxxx.streamlit.app`)

---

## 4. After deploy — quick checks

- [ ] Logo and title **Amina** show  
- [ ] Jollof demo works  
- [ ] Picking ingredients + moving time slider **keeps** selections  
- [ ] Recipe **Details** show measurements  
- [ ] **Save kitchen** updates the URL (bookmark to restore)

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| App crashes on import | Check Cloud logs; ensure `src/` and `data/` are in the repo |
| No images | Ensure `images/` was committed (not gitignored) |
| Old code on Cloud | Push again; Cloud redeploys on new commits to `main` |
| Git not found in PowerShell | Close and reopen terminal after install; or use GitHub Desktop |

## Do not commit

- `__pycache__/`, `.venv/`, `agent-tools/`, `terminals/`  
- Secrets (none required for Amina today)  
- `data/saved_pantry.json` (per-user; not used on Cloud anyway)
