# Lottery Optimizer — Streamlit Project

This canvas contains a ready-to-upload GitHub project for a Streamlit app that:

* Allows the user to upload an Excel file (Column A: tickets like `1,2,3,4,5,6`).
* Processes 6-number tickets (numbers 1–25).
* Brute-force searches all 177,100 possible 6-number combinations to find the one(s) with the lowest total payout using your payout rules.
* Applies tie-breaking preferences: prefer combos with exactly one 5-match and 4–5 four-matches.
* Shows the best 10 combinations and lets the user download results as CSV.

---

Below are the project files. Copy each file into your project folder `lottery_optimizer/`.

---

## `app.py`

```python
import streamlit as st
import pandas as pd
import itertools
import math
from collections import Counter
from io import StringIO
from utils import (validate_and_parse_tickets, evaluate_combo_payouts,
                   tie_score)

st.set_page_config(page_title="Lottery Optimizer", layout="wide")

st.title("🎯 Lottery Optimizer — Find Lowest Payout 6-number Combo (1–25)")
st.markdown(
    """
Upload an Excel file where **Column A** contains tickets (6 unique numbers, comma-separated).
The app will evaluate all 177,100 possible 6-number combinations (numbers 1..25) and show the best candidates.

**Payout rules** (built-in):
- 3 numbers matched → 15
- 4 numbers matched → 450
- 5 numbers matched → 1850
- 6 numbers matched → 50000

Preferences: the app prefers combinations with exactly one 5-match and 4–5 four-matches when payouts tie.
"""
)

with st.sidebar:
    st.header("Options")
    show_all = st.checkbox("Show full results (may be large)", value=False)
    max_display = st.number_input("How many top combos to display", min_value=1, max_value=500, value=10)
    run_button = st.button("Run search")

uploaded = st.file_uploader("Upload Excel file (xlsx)", type=["xlsx", "xls"])

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

    st.success(f"Loaded {len(tickets)} tickets.")

    if run_button:
        st.info("Starting brute-force search over 177,100 combinations — this may take a few seconds.")
        numbers = list(range(1, 26))
        min_payout = math.inf
        best = []  # store tuples (total, counts3, counts4, counts5, counts6, combo)

        progress_bar = st.progress(0)
        status_text = st.empty()

        total_combos = math.comb(25, 6)
        comb_idx = 0
        # iterate combinations
        for combo in itertools.combinations(numbers, 6):
            comb_idx += 1
            if comb_idx % 1000 == 0:
                progress_bar.progress(int(comb_idx / total_combos * 100))
                status_text.text(f"Evaluated {comb_idx}/{total_combos} combos...")

            total, counts = evaluate_combo_payouts(combo, tickets)

            # early pruning handled inside evaluate_combo_payouts via optional threshold
            if total < min_payout:
                min_payout = total
                best = [(total, counts[3], counts[4], counts[5], counts[6], combo)]
            elif total == min_payout:
                best.append((total, counts[3], counts[4], counts[5], counts[6], combo))

        progress_bar.progress(100)
        status_text.text("Search complete.")

        st.success(f"Minimum total payout found: {min_payout}")
        st.write(f"Number of combos achieving this minimum: {len(best)}")

        # Tie-breaker sort
        best_sorted = sorted(best, key=tie_score)

        rows = []
        for total, num3, num4, num5, num6, combo in best_sorted:
            rows.append({
                "combo": ",".join(map(str, combo)),
                "total_payout": total,
                "matches_3": num3,
                "matches_4": num4,
                "matches_5": num5,
                "matches_6": num6,
            })

        result_df = pd.DataFrame(rows)

        # Display top results
        st.subheader("Top combinations")
        if not result_df.empty:
            st.dataframe(result_df.head(max_display))
            csv = result_df.to_csv(index=False)
            st.download_button("Download results as CSV", data=csv, file_name="best_combos.csv")

            if show_all:
                st.write(result_df)
        else:
            st.warning("No combinations found — this should not happen.")

else:
    st.info("Upload an Excel file with tickets in Column A to begin.")
```

---

## `utils.py`

```python
# utils.py
import pandas as pd
from collections import Counter
import math

PAYOUT_MAP = {3: 15, 4: 450, 5: 1850, 6: 50000}


def validate_and_parse_tickets(df):
    """Validate and parse tickets from a DataFrame (first column expected).

    Returns a list of frozenset tickets.
    Raises ValueError on invalid format.
    """
    if df.shape[1] < 1:
        raise ValueError("Input file has no columns.")

    tickets_raw = df.iloc[:, 0].astype(str).tolist()
    tickets = []
    for i, row in enumerate(tickets_raw, start=1):
        parts = [p.strip() for p in str(row).split(",") if p.strip() != ""]
        if len(parts) != 6:
            raise ValueError(f"Row {i} does not contain 6 numbers: {row}")
        try:
            nums = [int(x) for x in parts]
        except ValueError:
            raise ValueError(f"Row {i} contains non-integer values: {row}")
        if any(n < 1 or n > 25 for n in nums):
            raise ValueError(f"Row {i} has numbers outside 1..25: {row}")
        if len(set(nums)) != 6:
            raise ValueError(f"Row {i} contains duplicate numbers: {row}")
        tickets.append(frozenset(nums))
    return tickets


def evaluate_combo_payouts(combo, tickets, current_best=math.inf):
    """Compute total payout for a given combo (tuple of 6 ints) against tickets.

    Returns (total_payout, counts) where counts is a Counter of matches.
    If total exceeds current_best during counting, it will return early with a value > current_best.
    """
    combo_set = set(combo)
    counts = Counter()
    total = 0
    for t in tickets:
        m = len(combo_set & t)
        counts[m] += 1
        if m >= 3:
            total += PAYOUT_MAP.get(m, 0)
        # early stop if already worse than best
        if total > current_best:
            # return an inflated total to signal prune
            return total, counts
    return total, counts


def tie_score(item):
    """Tie-breaker scoring: lower is better.

    Prefers exactly one 5-match; prefers num4 near 4–5; fewer 6-matches and fewer 3-matches.
    """
    _, num3, num4, num5, num6, combo = item
    score = abs(num5 - 1) * 1_000_000
    score += abs(num4 - 4.5) * 10_000
    score += num6 * 1000 + num3 * 1
    return score
```

---

## `requirements.txt`

```
streamlit>=1.0
pandas
```

---

## `README.md`

````markdown
# Lottery Optimizer (Streamlit)

This project is a Streamlit web app that finds a 6-number combination (1–25) that minimizes total payout against an uploaded set of tickets.

## Project structure

- `app.py` — Streamlit application
- `utils.py` — helper functions for parsing tickets and evaluating combinations
- `requirements.txt` — Python dependencies

## How to run locally

1. Create a virtual environment and activate it.
2. Install dependencies:

```bash
pip install -r requirements.txt
````

3. Run the app:

```bash
streamlit run app.py
```

4. Upload your Excel file (Column A — tickets like `1,2,3,4,5,6`) and click **Run search**.

## Deploy to Streamlit Cloud

1. Create a new GitHub repository and push this project.
2. Connect the repository in Streamlit Cloud.
3. Deploy — Streamlit Cloud will install dependencies from `requirements.txt`.

## Notes

* The brute-force search checks all `C(25,6)=177,100` combinations which is fast enough for typical use.
* If you have extremely large ticket files (many thousands of rows) the evaluation will take longer; consider batching or implementing optimizations.

```

---

### Next steps

- Copy these files into a `lottery_optimizer/` folder and push to GitHub.
- Then deploy on Streamlit Cloud or run locally with `streamlit run app.py`.

If you want, I can also:
- Generate a ready-to-download ZIP of the project.
- Add a GitHub Actions workflow for automated tests.
- Add performance optimizations (multithreading / numpy vectorization) if you expect >10k tickets.

Tell me which of the above you'd like and I will proceed.

```
