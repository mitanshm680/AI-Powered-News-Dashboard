import React, { useState } from 'react';
import { Article } from '../types';
import { formatArticleDate } from '../utils/dateUtils';
import ArticleModal from './ArticleModal';

interface NewsCardProps {
  article: Article;
  onSave: (id: string) => void;
  onShare: (article: Article) => void;
}

const NewsCard: React.FC<NewsCardProps> = ({ article, onSave, onShare }) => {
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleCardClick = () => {
    setIsModalOpen(true);
  };

  const handleModalClose = () => {
    setIsModalOpen(false);
  };

  return (
    <>
      <div 
        className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden transition-all duration-300 hover:shadow-lg h-full cursor-pointer"
        onClick={handleCardClick}
      >
        <div className="relative h-48">
          <img
            src={article.imageUrl}
            alt={article.title}
            className="absolute inset-0 w-full h-full object-cover"
          />
          <div className="absolute top-3 left-3">
            <span className="bg-blue-600 text-white text-xs px-2 py-1 rounded-md capitalize">
              {article.category}
            </span>
          </div>
        </div>
        
        <div className="p-4">
          <h2 className="text-lg font-bold text-gray-800 dark:text-white mb-2 line-clamp-2 leading-tight">
            {article.title}
          </h2>
          
          <p className="text-gray-600 dark:text-gray-300 mb-4 text-sm leading-relaxed line-clamp-3">
            {article.summary}
          </p>

          <div className="flex items-center justify-between mt-auto pt-2 border-t border-gray-100 dark:border-gray-700">
            <div className="text-sm text-gray-500 dark:text-gray-400">
              {formatArticleDate(article.publishedAt)}
            </div>
            <div className="flex space-x-2">
              <a
                href={article.fullArticleUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-400 hover:text-blue-600 dark:text-gray-500 dark:hover:text-blue-400 transition-colors"
                title="Open article in new tab"
                onClick={(e) => e.stopPropagation()} // Prevent card click when clicking link
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </a>
              <button
                onClick={(e) => {
                  e.stopPropagation(); // Prevent card click when clicking share
                  onShare(article);
                }}
                className="text-gray-400 hover:text-blue-600 dark:text-gray-500 dark:hover:text-blue-400 transition-colors"
                title="Share article"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
                </svg>
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation(); // Prevent card click when clicking save
                  onSave(article.id);
                }}
                className={`transition-colors ${
                  article.saved 
                    ? 'text-yellow-500 dark:text-yellow-400' 
                    : 'text-gray-400 hover:text-yellow-500 dark:text-gray-500 dark:hover:text-yellow-400'
                }`}
                title={article.saved ? 'Remove from saved' : 'Save article'}
              >
                <svg className="w-5 h-5" fill={article.saved ? 'currentColor' : 'none'} stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>

      {isModalOpen && (
        <ArticleModal
          article={article}
          onClose={handleModalClose}
          onSave={onSave}
          onShare={onShare}
        />
      )}
    </>
  );
};

export default NewsCard;