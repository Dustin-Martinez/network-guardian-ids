import json
import os
import sys
import time

packet = json.loads(sys.stdin.read())
mode = os.environ.get('BRIDGE_TEST_MODE', 'valid')
if mode == 'timeout':
    time.sleep(5)
elif mode == 'failure':
    print('BRIDGE_ERROR: Fixture model unavailable.', file=sys.stderr)
    sys.exit(1)
elif mode == 'malformed':
    print('this is not json')
elif mode == 'invalid':
    print(json.dumps({'prediction': 'normal', 'confidence': 999, 'is_threat': True, 'model': packet['model']}))
else:
    print('fixture diagnostic', file=sys.stderr)
    print(json.dumps({'prediction': 'dos', 'confidence': 75, 'is_threat': True, 'model': packet['model']}))
