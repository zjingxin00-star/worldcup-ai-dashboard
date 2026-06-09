import sys
sys.path.insert(0, 'd:/Claude/backend')
from scraper import fetch_real_matches

matches = fetch_real_matches(50)

# Show date distribution
dates = {}
for m in matches:
    d = m['time'][:10]
    dates[d] = dates.get(d, 0) + 1

print("Match dates:")
for d in sorted(dates):
    print(f"  {d}: {dates[d]} matches")

print("\nFirst 25 matches:")
for m in sorted(matches, key=lambda x: x['time'])[:25]:
    print(f"  {m['time']} | {m['homeTeam']} vs {m['awayTeam']} | {m['group']}")
