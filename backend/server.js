const express = require('express');
const cors = require('cors');
require('dotenv').config();

const legalRoutes = require('./routes/legalRoutes');

const app = express();

app.use(cors());
app.use(express.json({ limit: '25mb' }));

app.use('/api', legalRoutes);

const PORT = process.env.PORT || 5000;

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
