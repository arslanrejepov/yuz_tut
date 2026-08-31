import json
from collections import Counter

cats = Counter()
total_null = 0
with open('locations_merged.jsonl', encoding='utf-8') as f:
    for line in f:
        r = json.loads(line)
        if r['latitude'] is None or r['longitude'] is None:
            total_null += 1
            for c in r['categories']:
                cats[c] += 1

print('total null lat/long:', total_null)
print()
for cat, cnt in cats.most_common(20):
    print(f'{cnt:5d}  {cat}')