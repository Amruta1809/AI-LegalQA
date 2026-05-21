const axios = require('axios');
const { generateEmbedding } = require('./embeddingService');
const { searchLaws } = require('./searchService');
const { buildPrompt } = require('../utils/promptBuilder');

async function askQuestion(question) {
  try {
    // Generate embedding for query
    console.log('Generating embedding for question:', question);
    const queryEmbedding = await generateEmbedding(question);
    console.log('Embedding generated, length:', queryEmbedding?.length);

    // Search for relevant laws
    console.log('Searching for relevant laws...');
    let relevantLaws = [];
    try {
      relevantLaws = await searchLaws(queryEmbedding);
      console.log('Found laws:', relevantLaws?.length || 0);
    } catch (searchError) {
      console.error('Law search unavailable, continuing without citations:', searchError.message);
    }

    // Build prompt (with or without laws)
    const prompt = buildPrompt(question, relevantLaws);

    // Get completion
    console.log('Requesting completion from OpenRouter...');
    const completion = await axios.post(
      'https://openrouter.ai/api/v1/chat/completions',
      {
        model: 'openai/gpt-4o-mini',
        messages: [{ role: 'user', content: prompt }],
      },
      {
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${process.env.OPENROUTER_API_KEY}`,
          'HTTP-Referer': process.env.APP_URL || 'http://localhost:3171',
          'X-Title': 'AI Legal Q&A',
        },
        timeout: 30000,
      }
    );

    const answer = completion.data.choices[0].message.content;
    const fullAnswer = answer + "\n\nThis tool provides general legal information and is not legal advice.";

    // Extract citations (only if laws were found)
    const citations = (relevantLaws && relevantLaws.length > 0)
      ? relevantLaws.map(law => ({ act: law.act, section: law.section }))
      : [];

    return {
      answer: fullAnswer,
      citations,
    };
  } catch (error) {
    console.error('Error in askQuestion:', error.message);
    throw error;
  }
}

module.exports = { askQuestion };
