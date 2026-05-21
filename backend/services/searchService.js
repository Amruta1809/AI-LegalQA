const db = require('../config/database');
const { toVectorLiteral } = require('../utils/vector');

async function searchLaws(queryEmbedding, matchCount = 3) {
  try {
    const { rows } = await db.query(
      'SELECT content, act, section, similarity FROM match_laws($1::vector, $2::integer)',
      [toVectorLiteral(queryEmbedding), matchCount]
    );

    // Filter out low-similarity results
    const threshold = 0.5;
    const filtered = (rows || []).filter(law => law.similarity >= threshold);

    return filtered;
  } catch (error) {
    console.error('Search service error:', error.message);
    throw error;
  }
}

module.exports = { searchLaws };
