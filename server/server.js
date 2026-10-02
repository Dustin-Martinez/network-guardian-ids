const express = require('express');
const cors = require('cors');
const { spawn } = require('child_process');
const path = require('path');

const app = express();
app.use(cors());
app.use(express.json());

app.post('/api/analyze', (req, res) => {
    // Points up to root .venv/Scripts/python.exe
    const pythonExecutable = path.join(__dirname, '../.venv/Scripts/python.exe');
    const scriptPath = path.join(__dirname, 'predict_bridge.py');
    
    const pyProcess = spawn(pythonExecutable, [scriptPath]);

    let resultData = '';

    pyProcess.stdin.write(JSON.stringify(req.body));
    pyProcess.stdin.end();

    pyProcess.stdout.on('data', (data) => {
        resultData += data.toString();
    });

    pyProcess.on('close', (code) => {
        try {
            const jsonResult = JSON.parse(resultData);
            res.json(jsonResult);
        } catch (err) {
            res.status(500).json({ error: "Failed to parse Python model prediction." });
        }
    });
});

app.listen(5000, () => console.log('Node.js Server running on port 5000'));