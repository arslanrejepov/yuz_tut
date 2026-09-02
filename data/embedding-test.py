import json

with open('locations_embedding_ready.jsonl', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if i >= 3:
            break
        r = json.loads(line)
        print('---', r['id'])
        print(r['embedding_text'])
        print()