import sys
import json
import joblib
import numpy as np

def main():
    raw_input = sys.stdin.read()
    if not raw_input:
        return

    data = json.loads(raw_input)
    
    # Load model artifact from ../models/
    model = joblib.load("../models/xgboost_model.pkl")
    
    class_map = {0: 'normal', 1: 'dos', 2: 'probe', 3: 'r2l', 4: 'u2r'}
    features = np.array([list(data.values())])
    
    pred = model.predict(features)[0]
    probs = model.predict_proba(features)[0]

    output = {
        "prediction": class_map.get(pred, "unknown"),
        "confidence": round(float(np.max(probs)) * 100, 2),
        "is_threat": pred != 0
    }

    print(json.dumps(output))

if __name__ == "__main__":
    main()