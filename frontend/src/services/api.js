import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

export const askQuestion = async (question) => {
  const response = await axios.post(`${API_BASE_URL}/ask`, { question });
  return response.data;
};

export const fetchLaws = async (search = '') => {
  const params = search ? `?search=${encodeURIComponent(search)}` : '';
  const response = await axios.get(`${API_BASE_URL}/laws${params}`);
  return response.data;
};

function blobToDataUrl(blob) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => resolve(reader.result);
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
}

export const transcribeAudio = async (audioBlob, language) => {
  const audio = await blobToDataUrl(audioBlob);
  const response = await axios.post(`${API_BASE_URL}/voice/transcribe`, { audio, language });
  return response.data;
};

export const speakText = async (text) => {
  const response = await axios.post(
    `${API_BASE_URL}/voice/speak`,
    { text },
    { responseType: 'blob' }
  );
  return response.data;
};
