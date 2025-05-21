import React from 'react';
import { Bookmark, Share2, ExternalLink } from 'lucide-react';
import { Article } from '../types';
import { formatRelativeTime } from '../utils/dateUtils';

interface NewsCardProps {
  article: Article;
  onSave: (id: string) => void;
  onShare: (article: Article) => void;
}

const NewsCard: React.FC<NewsCardProps> = ({ article, onSave, onShare }) => {
  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden transition-all duration-300 hover:shadow-lg mb-6 max-w-lg mx-auto">
      <div className="relative h-52 w-full">
        <img
          src={article.imageUrl}
          alt={article.title}
          className="absolute inset-0 w-full h-full object-cover"
        />
        <div className="absolute top-3 left-3">
          <span className="bg-blue-900 text-white text-xs px-2 py-1 rounded-md capitalize">
            {article.category}
          </span>
        </div>
      </div>
      
      <div className="p-6">
        <h2 className="text-xl font-bold text-gray-800 mb-3 leading-tight">
          {article.title}
        </h2>
        
        <p className="text-gray-600 mb-4 text-sm leading-relaxed">
          {article.summary}
        </p>
        
        <div className="flex items-center justify-between mt-6">
          <div className="flex items-center space-x-4">
            <button 
              onClick={() => onSave(article.id)}
              className="text-gray-500 hover:text-blue-900 transition-colors"
              aria-label="Save article"
            >
              <Bookmark 
                className={`h-5 w-5 ${article.saved ? 'fill-blue-900 text-blue-900' : ''}`} 
              />
            </button>
            <button 
              onClick={() => onShare(article)}
              className="text-gray-500 hover:text-blue-900 transition-colors"
              aria-label="Share article"
            >
              <Share2 className="h-5 w-5" />
            </button>
          </div>
          
          <div className="flex items-center space-x-2">
            <span className="text-xs text-gray-500">{formatRelativeTime(article.publishedAt)}</span>
            <span className="text-xs text-gray-500">•</span>
            <span className="text-xs text-gray-500">{article.source}</span>
          </div>
        </div>
        
        <a
          href={article.fullArticleUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center mt-6 text-blue-900 font-medium text-sm hover:text-blue-700 transition-colors group"
        >
          Read full article 
          <ExternalLink className="h-4 w-4 ml-1 group-hover:translate-x-0.5 transition-transform" />
        </a>
      </div>
    </div>
  );
};

export default NewsCard;