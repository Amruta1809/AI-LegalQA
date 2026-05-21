const axios = require('axios');

async function generateEmbedding(text) {
  try {
    const headers = {
      'Content-Type': 'application/json',
    };
    if (process.env.HUGGINGFACE_API_KEY) {
      headers['Authorization'] = `Bearer ${process.env.HUGGINGFACE_API_KEY}`;
    }
    
    const response = await axios.post(
      'https://router.huggingface.co/hf-inference/models/sentence-transformers/all-MiniLM-L6-v2/pipeline/feature-extraction',
      { inputs: text },
      { headers, timeout: 15000 }
    );
    
    // Hugging Face may return nested arrays: [[...embedding...]]
    let embedding = response.data;
    
    // Unwrap nested arrays until we get a flat number array
    while (Array.isArray(embedding) && Array.isArray(embedding[0])) {
      embedding = embedding[0];
    }
    
    if (Array.isArray(embedding) && typeof embedding[0] === 'number') {
      return embedding;
    }
    
    throw new Error('Invalid embedding response');
  } catch (error) {
    console.error('Embedding error:', error.message);
    throw error;
  }
}

module.exports = { generateEmbedding };
