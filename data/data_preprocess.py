import json, re
from collections import defaultdict

def extract_building(addr):
    if not addr:
        return None
    m = re.search(r'"([^"]+)"', addr)
    if m:
        return m.group(1).strip().lower()
    return None

building_coords = defaultdict(list)
records = []

with open('locations_merged.jsonl', encoding='utf-8') as f:
    for line in f:
        r = json.loads(line)
        records.append(r)
        b = extract_building(r['address_tm'])
        if b and r['latitude'] is not None and r['longitude'] is not None:
            building_coords[b].append((r['latitude'], r['longitude']))

recoverable = 0
still_null = 0
for r in records:
    if r['latitude'] is None or r['longitude'] is None:
        b = extract_building(r['address_tm'])
        if b and b in building_coords:
            recoverable += 1
        else:
            still_null += 1

print('recoverable via building match:', recoverable)
print('still null after backfill:', still_null)
print('unique buildings found:', len(building_coords))