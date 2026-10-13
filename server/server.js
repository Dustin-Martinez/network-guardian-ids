'use strict';

const express = require('express');
const cors = require('cors');
const { spawn } = require('node:child_process');
const path = require('node:path');
const { validateRequest, errorResponse, RAW_FIELDS } = require('./validate');
const CLASSES = ['normal', 'dos', 'probe', 'r2l', 'u2r'];

function validPrediction(result, model) {
  return result && CLASSES.includes(result.prediction)
    && typeof result.confidence === 'number' && Number.isFinite(result.confidence)
    && result.confidence >= 0 && result.confidence <= 100
    && result.is_threat === (result.prediction !== 'normal')
    && result.model === model && !result.error;
}

function createApp(options = {}) {
  const app = express();
  const pythonExecutable = options.pythonExecutable || path.resolve(__dirname,
    process.platform === 'win32' ? '../.venv/Scripts/python.exe' : '../.venv/bin/python');
  const scriptPath = options.scriptPath || path.join(__dirname, 'predict_bridge.py');
  const timeoutMs = options.timeoutMs ?? 60000;
  app.use(cors({ origin: ['http://localhost:3000', 'http://127.0.0.1:3000'] }));
  app.use(express.json({ limit: '32kb' }));

  app.post('/api/analyze', (req, res) => {
    const validationError = validateRequest(req.body);
    const model = req.body?.model ?? 'xgboost';
    if (validationError) return res.status(400).json(errorResponse(validationError, model));
    // Forward only contract fields. Request key order never controls model order.
    const packet = Object.fromEntries(RAW_FIELDS.map(name => [name, req.body[name]]));
    packet.model = model;
    let child;
    let timer;
    let finished = false;
    let stdout = '';
    let stderr = '';
    const fail = message => {
      if (finished) return;
      finished = true;
      clearTimeout(timer);
      if (child && child.exitCode === null) child.kill();
      if (!res.destroyed) res.status(500).json(errorResponse(message, model));
    };
    try {
      child = spawn(pythonExecutable, [scriptPath], {
        cwd: __dirname, windowsHide: true,
        env: { ...process.env, ...options.bridgeEnv },
        stdio: ['pipe', 'pipe', 'pipe'],
      });
    } catch {
      fail('Unable to start Python bridge. Complete docs/SETUP.md first.');
      return;
    }
    timer = setTimeout(() => fail('Prediction timed out.'), timeoutMs);
    res.on('close', () => {
      if (!finished) {
        finished = true;
        clearTimeout(timer);
        child.kill();
      }
    });
    child.on('error', () => fail('Unable to start Python bridge. Complete docs/SETUP.md first.'));
    child.stdin.on('error', () => fail('Unable to send request to Python bridge.'));
    child.stdout.on('data', chunk => {
      stdout += chunk.toString();
      if (Buffer.byteLength(stdout) > 65536) fail('Invalid oversized prediction output.');
    });
    child.stderr.on('data', chunk => { stderr = (stderr + chunk.toString()).slice(-8192); });
    child.on('close', code => {
      if (finished) return;
      if (code !== 0) {
        const diagnostic = stderr.split(/\r?\n/).find(line => line.startsWith('BRIDGE_ERROR: '));
        fail(diagnostic ? diagnostic.slice('BRIDGE_ERROR: '.length) : 'Python bridge failed. Check server diagnostics.');
        return;
      }
      let result;
      try { result = JSON.parse(stdout); }
      catch { fail('Failed to parse Python model prediction.'); return; }
      if (!validPrediction(result, model)) {
        fail('Python returned an invalid prediction response.');
        return;
      }
      finished = true;
      clearTimeout(timer);
      res.json(result);
    });
    child.stdin.end(JSON.stringify(packet));
  });

  // Express JSON parser errors must use the same response envelope as the API.
  app.use((error, req, res, next) => {
    if (error.type === 'entity.parse.failed' || error.type === 'entity.too.large') {
      return res.status(400).json(errorResponse('Invalid or oversized JSON body.', req.body?.model));
    }
    if (error) return res.status(500).json(errorResponse('Request processing failed.', req.body?.model));
    next();
  });
  return app;
}

if (require.main === module) {
  const port = Number(process.env.PORT || 5000);
  createApp().listen(port, '127.0.0.1', () => console.log(`Node.js Server running on port ${port}`));
}
module.exports = { createApp };
