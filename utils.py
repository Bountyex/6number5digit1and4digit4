# utils.py
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