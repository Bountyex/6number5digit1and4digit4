import random
from itertools import combinations

# payout rules
PAYOUTS = {
    3: 15,
    4: 450,
    5: 1850,
    6: 50000,
}

def match_count(combo, ticket):
    return len(set(combo) & set(ticket))

def calculate_payout(combo, tickets):
    stats = {"m3": 0, "m4": 0, "m5": 0, "m6": 0}
    total = 0

    for t in tickets:
        m = match_count(combo, t)
        if m >= 3:
            total += PAYOUTS[m]
            stats[f"m{m}"] += 1

    return total, stats

def generate_random_combo():
    return sorted(random.sample(range(1, 25 + 1), 6))

def evaluate_best_combinations(tickets, attempts=50000, top_k=10):
    best = []

    for _ in range(attempts):
        combo = generate_random_combo()
        payout, stats = calculate_payout(combo, tickets)

        # prefer: exactly 1 ticket with 5-match
        pref_5match = (stats["m5"] == 1)

        # prefer: 4–5 tickets with 4-match
        pref_4match = (3 <= stats["m4"] <= 6)

        score = payout

        # apply preference boosters
        if pref_5match:
            score -= 2000
        if pref_4match:
            score -= 500

        best.append((combo, score, payout, stats))

    # sort by (score then payout)
    best_sorted = sorted(best, key=lambda x: (x[1], x[2]))

    final_output = []
    for item in best_sorted[:top_k]:
        combo, score, payout, stats = item
        final_output.append((combo, payout, stats))

    return final_output
