import axios from 'axios';

const API = axios.create({
  baseURL: 'http://localhost:8000', // URL FastAPI
});

export const askHerb = (payload) => API.post('/herb/ask', payload);
