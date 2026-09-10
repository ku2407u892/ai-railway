import axios from 'axios';
const API = axios.create({ baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000' });
API.interceptors.request.use(cfg => {
  const t = localStorage.getItem('token');
  if (t) cfg.headers.Authorization = `Bearer ${t}`;
  return cfg;
});
API.interceptors.response.use(r => r, err => {
  if (err.response?.status === 401) { localStorage.clear(); window.location.href = '/login'; }
  return Promise.reject(err);
});
export const getBlocks = () => API.get('/blocks/');
export const updateBlockStatus = (id, status) => API.put(`/blocks/${id}/status?status=${status}`);
export const getTrains = () => API.get('/trains/');
export const predictDelay = (id) => API.get(`/trains/${id}/predict-delay`);
export const assignBlock = (trainId, blockId) => API.put(`/trains/${trainId}/assign-block?block_id=${blockId}`);
export const getAlerts = () => API.get('/alerts/');
export const acknowledgeAlert = (id) => API.post(`/alerts/${id}/acknowledge`);
export const getSuggestions = () => API.get('/optimization/suggestions');
export const executeOptimization = () => API.post('/optimization/execute');
export const getSystemStatus = () => API.get('/optimization/system-status');
export default API;
