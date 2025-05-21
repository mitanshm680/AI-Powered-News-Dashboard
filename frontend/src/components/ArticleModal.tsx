import React from 'react';
import { Article } from '../types';
import { formatArticleDate } from '../utils/dateUtils';

interface ArticleModalProps {
  article: Article;
  onClose: () => void;
  onSave: (id: string) => void;
  onShare: (article: Article) => void;
}

const ArticleModal: React.FC<ArticleModalProps> = ({ article, onClose, onSave, onShare }) => {
  // Prevent click inside modal from closing it
  const handleModalClick = (e: React.MouseEvent) => {
    e.stopPropagation();
  };

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden"
        onClick={handleModalClick}
      >
        <div className="relative h-96">
          <img
            src={article.imageUrl}
            alt={article.title}
            className="absolute inset-0 w-full h-full object-cover"
          />
          <div className="absolute top-4 right-4">
            <button
              onClick={onClose}
              className="bg-black bg-opacity-50 text-white rounded-full p-2 hover:bg-opacity-75 transition-all"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <div className="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black to-transparent p-6">
            <span className="bg-blue-600 text-white text-sm px-3 py-1 rounded-full capitalize">
              {article.category}
            </span>
            <h1 className="text-white text-2xl font-bold mt-2">{article.title}</h1>
          </div>
        </div>

        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="text-sm text-gray-500">
              {formatArticleDate(article.publishedAt)} • {article.source}
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => onShare(article)}
                className="text-gray-400 hover:text-blue-600 transition-colors p-2"
                title="Share article"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
                </svg>
              </button>
              <button
                onClick={() => onSave(article.id)}
                className={`transition-colors p-2 ${article.saved ? 'text-yellow-500' : 'text-gray-400 hover:text-yellow-500'}`}
                title={article.saved ? 'Remove from saved' : 'Save article'}
              >
                <svg className="w-5 h-5" fill={article.saved ? 'currentColor' : 'none'} stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
                </svg>
              </button>
            </div>
          </div>

          <p className="text-gray-600 text-base leading-relaxed mb-6">
            {article.summary}
          </p>

          <div className="flex justify-center">
            <a
              href={article.fullArticleUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Read full article
              <svg className="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ArticleModal; 