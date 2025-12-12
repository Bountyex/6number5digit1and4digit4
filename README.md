
## 📌 FILE 4 — `README.md`

```markdown
# Lottery Optimizer (Streamlit)

This Streamlit app searches all 177100 possible 6-number combinations (1–25) and finds the one(s) generating the lowest payout according to:
- 3 matches = 15
- 4 matches = 450
- 5 matches = 1850
- 6 matches = 50000

## How to Run

### Local
```

pip install -r requirements.txt
streamlit run app.py

```

### Streamlit Cloud Deployment
1. Upload this folder to GitHub.
2. Go to https://streamlit.io/cloud.
3. Create a new app from the GitHub repo.
4. Deploy.

## File Format
Upload an Excel file where Column A contains entries like:
```

1,2,3,4,5,6

```

## Features
- Validates tickets
- Brute-force evaluates all 177100 combos
- Tie-breaker preference for 1×5-match and 4–5×4-match
- Shows top results and allows CSV download
```

---

Your **full GitHub-ready Streamlit project** is now complete.

If you want a downloadable ZIP file of this project, tell me: **"Give me ZIP"**.
