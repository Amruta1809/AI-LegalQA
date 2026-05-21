require('dotenv').config();
const { generateEmbedding } = require('../backend/services/embeddingService');
const db = require('../backend/config/database');
const { toVectorLiteral } = require('../backend/utils/vector');

async function run() {
  const { rows: laws } = await db.query('SELECT id, content, embedding FROM laws ORDER BY id ASC');

  for (const law of laws) {
    if (!law.embedding) {
      try {
        const embedding = await generateEmbedding(law.content);
        await db.query(
          'UPDATE laws SET embedding = $1::vector WHERE id = $2',
          [toVectorLiteral(embedding), law.id]
        );
        console.log("Updated:", law.id);
      } catch (err) {
        console.error('Error updating law:', law.id, err);
      }
    }
  }
  console.log('Embedding generation complete.');
}

run();
