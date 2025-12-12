# Lottery Optimizer — Streamlit Project (Clean, GitHub-Ready)

Below is the complete, cleaned, ASCII-safe, ready-to-upload project for GitHub + Streamlit Cloud.

Copy these files exactly into a folder named `lottery_optimizer/`.

---

## 📌 FILE 1 — `app.py`

```python
import streamlit as st
import pandas as pd
import itertools
import math
from collections import Counter
from utils import validate_and_parse_tickets, evaluate_combo_payouts, tie_score

st.set_page_config(page_title="Lottery Optimizer", layout="wide")

st.title("Lottery Optimizer – Lowest Payout Finder (6 Numbers, 1–25)")
st.markdown(
    """
Upload an Excel file containing 6-number lottery tickets.
Each row in Column A must contain tickets like:
```

1,2,3,4,5,6

```

Payout rules:
- 3 matches = 15
- 4 matches = 450
- 5 matches = 1850
- 6 matches = 50000

The tool checks all 177100 combinations (1–25 choose 6) and finds the lowest payout combination.
Tie-breaker preferences:
- Prefer exactly 1 ticket with 5 matches
- Prefer 4–5 tickets with 4 matches
"""
)

with st.sidebar:
    st.header("Options")
    show_all = st.checkbox("Show all results", value=False)
    max_display = st.number_input(
        "Top combinations to display", min_value=1, max_value=200, value=10
    )
    run_button = st.button("Run Search")

uploaded = st.file_uploader("Upload Excel file", type=["xlsx", "xls"])

if uploaded is not None:
    try:
        df = pd.read_excel(uploaded, header=None)
    except Exception as e:
        st.error(f"Unable to read Excel file: {e}")
        st.stop()

    try:
        tickets = validate_and_parse_tickets(df)
    except ValueError as e:
        st.error(str(e))
        st.stop()

    st.success(f"Loaded {len(tickets)} valid tickets.")

    if run_button:
        st.info("Searching all 177100 combinations. Please wait...")

        numbers = list(range(1, 26))
        min_payout = math.inf
        best = []

        total_combos = math.comb(25, 6)
        progress = st.progress(0)
        status = st.empty()
        checked = 0

        for combo in itertools.combinations(numbers, 6):
            checked += 1
            if checked % 1000 == 0:
                progress.progress(int(checked / total_combos * 100))
                status.text(f"Evaluated {checked} / {total_combos} combinations...")

            total, counts = evaluate_combo_payouts(combo, tickets, min_payout)

            if total < min_payout:
                min_payout = total
                best = [(total, counts[3], counts[4], counts[5], counts[6], combo)]
            elif total == min_payout:
                best.append((total, counts[3], counts[4], counts[5], counts[6], combo))

        progress.progress(100)
        status.text("Search complete.")

        st.success(f"Minimum payout found: {min_payout}")
        st.write(f"Combinations with minimum payout: {len(best)}")

        # sort using tie-break preferences
        best_sorted = sorted(best, key=tie_score)

        rows = []
        for total, m3, m4, m5, m6, combo in best_sorted:
            rows.append({
                "combo": ",".join(map(str, combo)),
                "total_payout": total,
                "matches_3": m3,
                "matches_4": m4,
                "matches_5": m5,
                "matches_6": m6,
            })

        result_df = pd.DataFrame(rows)

        st.subheader("Top Results")
        st.dataframe(result_df.head(max_display))

        csv = result_df.to_csv(index=False)
        st.download_button("Download All Results (CSV)", csv, "best_combos.csv")

        if show_all:
            st.subheader("All Matching Combinations")
            st.dataframe(result_df)

else:
    st.info("Upload an Excel file to begin.")
```

---

## 📌 FILE 2 — `utils.py`

```python
from collections import Counter
import math

PAYOUT_MAP = {3: 15, 4: 450, 5: 1850, 6: 50000}

def validate_and_parse_tickets(df):
    tickets_raw = df.iloc[:, 0].astype(str).tolist()
    tickets = []

    for i, row in enumerate(tickets_raw, start=1):
        parts = [x.strip() for x in row.split(",") if x.strip() != ""]
        if len(parts) != 6:
            raise ValueError(f"Row {i} does not contain 6 numbers: {row}")

        try:
            nums = [int(x) for x in parts]
        except:
            raise ValueError(f"Row {i} contains non-integer values: {row}")

        if any(n < 1 or n > 25 for n in nums):
            raise ValueError(f"Row {i} contains numbers outside 1–25: {row}")

        if len(set(nums)) != 6:
            raise ValueError(f"Row {i} has duplicate numbers: {row}")

        tickets.append(frozenset(nums))

    return tickets


def evaluate_combo_payouts(combo, tickets, current_best):
    combo_set = set(combo)
    counts = Counter()
    total = 0

    for t in tickets:
        m = len(combo_set & t)
        counts[m] += 1
        if m >= 3:
            total += PAYOUT_MAP[m]

        if total > current_best:
            return total, counts

    return total, counts


def tie_score(item):
    total, m3, m4, m5, m6, combo = item
    score = abs(m5 - 1) * 1000000
    score += abs(m4 - 4.5) * 10000
    score += m6 * 1000
    score += m3
    return score
```

---

## 📌 FILE 3 — `requirements.txt`

```
streamlit
pandas
openpyxl
```

---

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
