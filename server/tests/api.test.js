const test = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');
const { createApp } = require('../server');
const { validateRequest, RAW_FIELDS } = require('../validate');
const sample = require('../examples/normal-smtp.json');
const fixture = path.join(__dirname, 'fixtures/bridge.py');

async function serve(options, run) {
  const server = createApp(options).listen(0, '127.0.0.1');
  await new Promise(resolve => server.once('listening', resolve));
  try { await run(`http://127.0.0.1:${server.address().port}`); }
  finally { server.closeAllConnections(); await new Promise(resolve => server.close(resolve)); }
}
async function post(url, body) {
  const res = await fetch(url + '/api/analyze', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: typeof body === 'string' ? body : JSON.stringify(body),
  });
  return { status: res.status, body: await res.json() };
}
function envelope(body) {
  assert.equal(body.prediction, 'normal');
  assert.equal(body.confidence, 0);
  assert.equal(body.is_threat, false);
  assert.equal(typeof body.error, 'string');
}

test('all 31 contract fields and every boundary rule are validated', () => {
  assert.equal(RAW_FIELDS.length, 31);
  assert.equal(validateRequest(sample), null);
  for (const name of RAW_FIELDS) {
    const packet = { ...sample }; delete packet[name];
    assert.ok(validateRequest(packet), name);
  }
  for (const patch of [
    { service: ' ' }, { flag: 1 }, { protocol_type: 'sctp' }, { model: null },
    { model: 'unknown' }, { land: 2 }, { logged_in: true },
    { src_bytes: -1 }, { duration: '0' }, { dst_bytes: Infinity },
    { same_srv_rate: -0.01 }, { dst_host_srv_rerror_rate: 1.01 },
  ]) assert.ok(validateRequest({ ...sample, ...patch }));
  assert.ok(validateRequest([]));
});

test('invalid and malformed requests use HTTP 400 without invoking Python', async () => {
  await serve({ pythonExecutable: '/missing/python' }, async url => {
    for (const body of [{}, [], '{', { ...sample, model: 'invalid' }]) {
      const result = await post(url, body);
      assert.equal(result.status, 400); envelope(result.body);
    }
  });
});

test('oversized JSON uses the error envelope', async () => {
  await serve({}, async url => {
    const result = await post(url, { ...sample, service: 'x'.repeat(40000) });
    assert.equal(result.status, 400); envelope(result.body);
  });
});

test('successful subprocess returns percentage, model and threat fields', async () => {
  await serve({ scriptPath: fixture }, async url => {
    for (const model of [undefined, 'random_forest', 'tabnet']) {
      const result = await post(url, { ...sample, ...(model ? { model } : {}) });
      assert.equal(result.status, 200);
      assert.deepEqual(result.body, { prediction: 'dos', confidence: 75, is_threat: true, model: model || 'xgboost' });
    }
  });
});

test('Python startup failure is HTTP 500', async () => {
  await serve({ pythonExecutable: path.join(__dirname, 'nonexistent-python.exe') }, async url => {
    const result = await post(url, sample);
    assert.equal(result.status, 500); envelope(result.body);
  });
});

for (const mode of ['failure', 'malformed', 'invalid', 'timeout']) {
  test(`bridge ${mode} is HTTP 500 with a structured error`, async () => {
    await serve({ scriptPath: fixture, bridgeEnv: { BRIDGE_TEST_MODE: mode }, timeoutMs: mode === 'timeout' ? 150 : 10000 }, async url => {
      const result = await post(url, { ...sample, model: 'random_forest' });
      assert.equal(result.status, 500); envelope(result.body);
      assert.equal(result.body.model, 'random_forest');
    });
  });
}

test('real bridge reports an unavailable model instead of a fake prediction', async () => {
  await serve({ bridgeEnv: { IDS_MODEL_DIR: path.join(__dirname, 'missing-models') } }, async url => {
    const result = await post(url, sample);
    assert.equal(result.status, 500); envelope(result.body);
    assert.match(result.body.error, /Model unavailable/);
  });
});
