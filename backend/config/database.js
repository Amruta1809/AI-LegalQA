const { neon } = require('@neondatabase/serverless');

if (!process.env.DATABASE_URL) {
  throw new Error('DATABASE_URL is required to connect to Neon PostgreSQL.');
}

const sql = neon(process.env.DATABASE_URL);

async function query(text, params = []) {
  const rows = await sql.query(text, params);
  return { rows };
}

module.exports = {
  sql,
  query,
};
