import json

def jprint(obj):
    text = json.dumps(obj, sort_keys=False, indent=3)
    print(text)
