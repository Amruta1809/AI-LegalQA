function CitationCard({ citation }) {
  return (
    <div className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-gray-700/50 border border-gray-700 rounded-lg text-xs text-gray-300">
      <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
        <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
      </svg>
      <span className="font-medium">{citation.act}</span>
      <span className="text-gray-500">§{citation.section}</span>
    </div>
  );
}

export default CitationCard;
