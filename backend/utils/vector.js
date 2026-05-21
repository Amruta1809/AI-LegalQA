function toVectorLiteral(values) {
  if (!Array.isArray(values) || values.length === 0) {
    throw new Error('Vector value must be a non-empty array.');
  }

  return `[${values.join(',')}]`;
}

module.exports = { toVectorLiteral };
