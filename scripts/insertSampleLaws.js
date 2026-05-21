require('dotenv').config();
const db = require('../backend/config/database');

const sampleLaws = [
  {
    act: "Information Technology Act 2000",
    section: "66",
    title: "Computer hacking and unauthorized access",
    content: "Whoever, with intent to cause or knowing that he is likely to cause wrongful loss or damage to the public or any person, by entering into any computer resource without authorization or exceeding authorized access",
    keywords: ["hacking", "unauthorized access", "computer crime"]
  },
  {
    act: "Indian Penal Code",
    section: "420",
    title: "Cheating and dishonestly inducing delivery",
    content: "Whoever cheats and by virtue of that cheating dishonestly induces the person deceived to deliver any property to any person",
    keywords: ["cheating", "fraud", "deception"]
  },
  {
    act: "Industrial Disputes Act 1947",
    section: "25",
    title: "Notice of termination",
    content: "No employer shall terminate the service of a workman except for some misconduct. The employer must give one month notice.",
    keywords: ["notice period", "termination", "employment"]
  }
];

async function insertData() {
  for (const law of sampleLaws) {
    try {
      await db.query(
        `
          INSERT INTO laws (act, section, title, content, keywords)
          VALUES ($1, $2, $3, $4, $5)
        `,
        [law.act, law.section, law.title, law.content, law.keywords]
      );
      console.log('Inserted:', law.section);
    } catch (error) {
      console.error('Insert error:', error.message);
    }
  }
  console.log('Done!');
  process.exit(0);
}

insertData().catch(err => {
  console.error('Error:', err);
  process.exit(1);
});
