# Amina

**Wetin we go cook today?**  
A Nigerian kitchen companion: tick what you have, get realistic dish suggestions with amounts and steps.

Built with [Streamlit](https://streamlit.io). Named **Amina** — a Northern Nigerian kitchen companion.

## Run locally

```powershell
cd path\to\Amina
python -m pip install -r requirements-dev.txt
streamlit run app.py
```

Or on Windows: `.\start.ps1` (sets local dev mode).

Open http://localhost:8501

## Deploy (Streamlit Community Cloud)

1. Push this repo to GitHub (see below).
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. **New app** → select this repository.
4. **Main file path:** `app.py`
5. Deploy.

Do **not** set `AMINA_DEV=1` on Cloud (that flag is only for local hot-reload).

## Project layout

| Path | Purpose |
|------|---------|
| `app.py` | Streamlit entry point |
| `src/` | Matching, UI, pantry, selection state |
| `data/` | Recipes + ingredient config (JSON) |
| `images/` | Dish photos |
| `assets/` | Logo + favicon |
| `tests/` | Unit tests |

## Save kitchen

Pantry is stored in the **browser URL** (`?pantry=...`) so each user has their own kitchen on shared hosting. Bookmark the page after **Save kitchen** to restore later.

## Tests

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest tests -q
```

## License / photos

Food photos from [Wikimedia Commons](https://commons.wikimedia.org/wiki/Category:Cuisine_of_Nigeria) (CC licenses). Use your own judgment in the kitchen.
