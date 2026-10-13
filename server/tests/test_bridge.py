"""Feature and inference checks without running model training or evaluation."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import joblib
import numpy as np

SERVER = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SERVER))
import predict_bridge as bridge


class ProbabilityModel:
    # Deliberately reversed class order to catch argmax decoding errors.
    classes_ = np.array([4, 3, 2, 1, 0])

    def predict_proba(self, frame):
        return np.array([[0.80, 0.05, 0.05, 0.05, 0.05]])


class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.packet = json.loads((SERVER / 'examples/normal-smtp.json').read_text())

    def test_feature_order_log_and_frozen_encodings(self):
        frame = bridge.prepare_features(self.packet)
        reordered = bridge.prepare_features(dict(reversed(list(self.packet.items()))))
        np.testing.assert_array_equal(frame.to_numpy(), reordered.to_numpy())
        self.assertEqual(frame.shape, (1, 43))
        for name in ['duration', 'src_bytes', 'dst_bytes']:
            self.assertAlmostEqual(frame[name].iloc[0], np.log1p(self.packet[name]))
        self.assertEqual(frame.protocol_type_tcp.iloc[0], 1)
        self.assertEqual(frame.flag_SF.iloc[0], 1)
        frequency = joblib.load(bridge.PROCESSED / 'encoder_service.pkl')
        self.assertEqual(frame.service_freq.iloc[0], frequency.frequencies_['smtp'])
        unknown = bridge.prepare_features({**self.packet, 'service': '__unseen__', 'flag': '__unseen__'})
        self.assertEqual(unknown.service_freq.iloc[0], 0)
        self.assertEqual(unknown.filter(like='flag_').to_numpy().sum(), 0)

    def test_probability_columns_follow_model_classes(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            joblib.dump(ProbabilityModel(), directory / 'rf_baseline.joblib')
            meta = {'class_order': bridge.CLASSES, 'feature_names': list(bridge.prepare_features(self.packet).columns), 'n_features': 43}
            (directory / 'rf_baseline.meta.json').write_text(json.dumps(meta))
            with patch.object(bridge, 'MODEL_DIR', directory):
                result = bridge.predict({**self.packet, 'model': 'random_forest'})
                self.assertEqual(result['prediction'], 'u2r')
                self.assertEqual(result['confidence'], 80)
                self.assertTrue(result['is_threat'])
                meta['feature_names'] = list(reversed(meta['feature_names']))
                (directory / 'rf_baseline.meta.json').write_text(json.dumps(meta))
                with self.assertRaisesRegex(ValueError, 'ordering'):
                    bridge.predict({**self.packet, 'model': 'random_forest'})

    def test_tabnet_requires_confirmed_scaling(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            (directory / 'tabnet_best.zip').write_bytes(b'not a real model')
            meta = {'class_order': bridge.CLASSES, 'feature_names': list(bridge.prepare_features(self.packet).columns)}
            (directory / 'tabnet_best.meta.json').write_text(json.dumps(meta))
            with patch.object(bridge, 'MODEL_DIR', directory):
                with self.assertRaisesRegex(ValueError, 'scaling requires Kit confirmation'):
                    bridge.predict({**self.packet, 'model': 'tabnet'})


if __name__ == '__main__':
    unittest.main()
