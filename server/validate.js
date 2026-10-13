'use strict';

const MODELS = ['random_forest', 'xgboost', 'tabnet'];
const NUMERIC_FIELDS = [
  'duration', 'src_bytes', 'dst_bytes', 'land', 'wrong_fragment', 'urgent',
  'hot', 'num_failed_logins', 'logged_in', 'root_shell', 'su_attempted',
  'num_root', 'num_file_creations', 'num_shells', 'num_access_files',
  'is_guest_login', 'count', 'srv_count', 'same_srv_rate', 'diff_srv_rate',
  'srv_diff_host_rate', 'dst_host_count', 'dst_host_same_srv_rate',
  'dst_host_diff_srv_rate', 'dst_host_same_src_port_rate',
  'dst_host_srv_diff_host_rate', 'dst_host_srv_serror_rate',
  'dst_host_srv_rerror_rate',
];
const BINARY_FIELDS = ['land', 'logged_in', 'root_shell', 'is_guest_login'];
const RAW_FIELDS = ['protocol_type', 'service', 'flag', ...NUMERIC_FIELDS];

function validateRequest(body) {
  if (!body || typeof body !== 'object' || Array.isArray(body)) {
    return 'Request must be a JSON object.';
  }
  if (body.model !== undefined && !MODELS.includes(body.model)) {
    return 'model must be random_forest, xgboost, or tabnet.';
  }
  if (!['tcp', 'udp', 'icmp'].includes(body.protocol_type)) {
    return 'protocol_type must be tcp, udp, or icmp.';
  }
  for (const name of ['service', 'flag']) {
    if (typeof body[name] !== 'string' || !body[name].trim()) {
      return `${name} must be a non-empty string.`;
    }
  }
  for (const name of NUMERIC_FIELDS) {
    if (typeof body[name] !== 'number' || !Number.isFinite(body[name])) {
      return `${name} must be a finite number.`;
    }
    if (name.endsWith('_rate') && (body[name] < 0 || body[name] > 1)) {
      return `${name} must be between 0 and 1.`;
    }
  }
  for (const name of BINARY_FIELDS) {
    if (![0, 1].includes(body[name])) return `${name} must be 0 or 1.`;
  }
  for (const name of ['duration', 'src_bytes', 'dst_bytes']) {
    if (body[name] < 0) return `${name} must be non-negative.`;
  }
  return null;
}

function errorResponse(error, model) {
  return {
    prediction: 'normal', confidence: 0, is_threat: false,
    model: MODELS.includes(model) ? model : 'xgboost', error,
  };
}

module.exports = { validateRequest, errorResponse, MODELS, RAW_FIELDS };
