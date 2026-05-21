function isGreeting(question) {
  if (!question) {
    return false;
  }

  const normalized = question.trim().toLowerCase();

  return /^(hi|hello|hey|hii+|good morning|good afternoon|good evening)([!.?, ]*)$/.test(normalized);
}

function buildPrompt(question, relevantLaws) {
  if (relevantLaws && relevantLaws.length > 0) {
    const context = relevantLaws
      .map(law => `Act: ${law.act}\nSection: ${law.section}\nContent: ${law.content}`)
      .join('\n\n');

    return `You are a legal AI assistant.
Answer ONLY from the provided legal context.
Do not invent information.
If answer is missing, say 'Not found in provided laws.'
Always include act and section when available.
Keep response simple for normal users.

Question: ${question}

Context:
${context}

Answer:`;
  }

  if (isGreeting(question)) {
    return `You are a friendly legal AI assistant specializing in Indian law.
The user has sent only a greeting.
Respond warmly in 1-2 short sentences and mention that you can help with legal questions about Indian law.
Do not give a legal explanation unless the user asks one.

Question: ${question}

Answer:`;
  }

  // Fallback: no laws in database, use LLM general knowledge
  return `You are a legal AI assistant specializing in Indian law.
The user's message is not a greeting.
Answer the user's actual question directly.
If no matching laws were found in the database, use your general legal knowledge and clearly mention that the answer is based on general legal knowledge, not retrieved law text.
Do not start with a greeting unless the user only greeted you.
Keep response simple for normal users.

Question: ${question}

Answer:`;
}

module.exports = { buildPrompt };
