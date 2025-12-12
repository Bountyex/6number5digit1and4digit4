import streamlit as st
import pandas as pd
from optimizer import evaluate_best_combinations

st.title("🎯 6-Number Lottery Lowest Payout Optimizer")

st.write("""
Upload an Excel file where **Column A** contains tickets (6 unique numbers between 1–25).
Example ticket format: `1,2,3,4,5,6`

The system will search for combinations that result in the **lowest payout**:
- 3 matches → 15  
- 4 matches → 450  
- 5 matches → 1850  
- 6 matches → 50000  
""")

uploaded = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded:
    df = pd.read_excel(uploaded)

    if df.shape[1] < 1:
        st.error("File must contain at least 1 column with tickets.")
        st.stop()

    tickets_raw = df.iloc[:, 0].dropna().astype(str).tolist()

    tickets = []
    for t in tickets_raw:
        try:
            nums = list(map(int, t.split(",")))
            if len(nums) == 6:
                tickets.append(nums)
        except:
            pass

    if len(tickets) == 0:
        st.error("No valid 6-number tickets found.")
        st.stop()

    st.success(f"Loaded {len(tickets)} tickets successfully!")

    st.write("⏳ Searching best combinations...")

    best_results = evaluate_best_combinations(tickets, top_k=10)

    st.subheader("🏆 Best 10 Combinations Found")

    for i, item in enumerate(best_results, start=1):
        combo, payout, stats = item

        st.write(f"### {i}. Combination: {combo}")
        st.write(f"💰 Total Payout: **{payout}**")
        st.write(f"🔍 Matches: 3→{stats['m3']}, 4→{stats['m4']}, 5→{stats['m5']}, 6→{stats['m6']}")
        st.write("---")

else:
    st.info("Please upload an Excel file to begin.")
