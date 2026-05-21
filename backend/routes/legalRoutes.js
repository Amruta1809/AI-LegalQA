const express = require('express');
const router = express.Router();
const db = require('../config/database');
const { fallbackLaws } = require('../data/fallbackLaws');
const { askQuestion } = require('../services/llmService');
const { synthesizeSpeech, transcribeAudio } = require('../services/voiceService');

function filterAndGroupLaws(laws, search = '') {
  const normalizedSearch = search.trim().toLowerCase();

  const filtered = normalizedSearch
    ? laws.filter((law) => {
        const haystack = [
          law.act,
          law.section,
          law.title,
          law.content,
          ...(law.keywords || []),
        ]
          .filter(Boolean)
          .join(' ')
          .toLowerCase();

        return haystack.includes(normalizedSearch);
      })
    : laws;

  const grouped = {};
  filtered.forEach((law) => {
    if (!grouped[law.act]) {
      grouped[law.act] = [];
    }
    grouped[law.act].push(law);
  });

  return { grouped, total: filtered.length };
}

router.post('/ask', async (req, res) => {
  try {
    const { question } = req.body;
    
    if (!question || question.trim() === '') {
      return res.status(400).json({ error: 'Question is required' });
    }

    console.log('API request received:', question);
    const result = await askQuestion(question);
    res.json(result);
  } catch (error) {
    console.error('API error:', error);
    res.status(500).json({ error: error.message || 'Something went wrong' });
  }
});

router.get('/laws', async (req, res) => {
  const search = typeof req.query.search === 'string' ? req.query.search : '';

  try {
    const params = [];
    let sql = `
      SELECT id, act, section, title, content, keywords
      FROM laws
    `;

    if (search.trim()) {
      params.push(`%${search.trim()}%`);
      sql += `
        WHERE title ILIKE $1
          OR content ILIKE $1
          OR act ILIKE $1
          OR section ILIKE $1
      `;
    }

    sql += ' ORDER BY act ASC, section ASC';

    const { rows } = await db.query(sql, params);
    const { grouped, total } = filterAndGroupLaws(rows, '');
    return res.json({ laws: grouped, total, source: 'database' });
  } catch (error) {
    console.error('Laws API fallback activated:', error.message);
    const { grouped, total } = filterAndGroupLaws(fallbackLaws, search);
    return res.json({ laws: grouped, total, source: 'fallback' });
  }
});

router.post('/voice/transcribe', async (req, res) => {
  try {
    const { audio, language } = req.body;

    if (!audio) {
      return res.status(400).json({ error: 'Audio is required.' });
    }

    const text = await transcribeAudio(audio, language);
    res.json({ text });
  } catch (error) {
    console.error('Voice transcription error:', error.message);
    res
      .status(error.status || 500)
      .json({ error: error.message || 'Voice transcription failed.', code: error.code });
  }
});

router.post('/voice/speak', async (req, res) => {
  try {
    const { text } = req.body;

    if (!text || !text.trim()) {
      return res.status(400).json({ error: 'Text is required.' });
    }

    const audioBuffer = await synthesizeSpeech(text);
    res.setHeader('Content-Type', 'audio/mpeg');
    res.setHeader('Content-Length', audioBuffer.length);
    res.send(audioBuffer);
  } catch (error) {
    console.error('Voice synthesis error:', error.message);
    res
      .status(error.status || 500)
      .json({ error: error.message || 'Voice synthesis failed.', code: error.code });
  }
});

module.exports = router;
