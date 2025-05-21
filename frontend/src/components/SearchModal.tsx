import React, { useState, useRef, useEffect, useCallback } from 'react';
import { X, Search } from 'lucide-react';
import { Article, articlesApi } from '../services/api';
import NewsCard from './NewsCard';

interface SearchModalProps {
  onClose: () => void;
  onSaveArticle: (id: string) => void;
  onShareArticle: (article: Article) => void;
}

const SearchModal: React.FC<SearchModalProps> = ({ onClose, onSaveArticle, onShareArticle }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const modalRef = useRef<HTMLDivElement>(null);
  const searchTimeout = useRef<number>();

  const handleSearch = useCallback(async (query: string) => {
    if (!query.trim()) {
      setArticles([]);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      console.log('Searching for:', query);
      const response = await articlesApi.searchArticles({
        q: query,
        pageSize: 10
      });
      console.log('Search response:', response);
      setArticles(response.articles || []);
    } catch (err) {
      console.error('Search error:', err);
      setError(err instanceof Error ? err.message : 'Failed to search articles');
    } finally {
      setLoading(false);
    }
  }, []);

  // Debounced search effect
  useEffect(() => {
    if (searchTimeout.current) {
      clearTimeout(searchTimeout.current);
    }

    searchTimeout.current = window.setTimeout(() => {
      handleSearch(searchQuery);
    }, 300); // 300ms delay

    return () => {
      if (searchTimeout.current) {
        clearTimeout(searchTimeout.current);
      }
    };
  }, [searchQuery, handleSearch]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      if (searchTimeout.current) {
        clearTimeout(searchTimeout.current);
      }
      handleSearch(searchQuery);
    }
  };

  const handleBackgroundClick = (e: React.MouseEvent) => {
    if (modalRef.current && !modalRef.current.contains(e.target as Node)) {
      onClose();
    }
  };

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-start justify-center pt-20 px-4"
      onClick={handleBackgroundClick}
    >
      <div
        ref={modalRef}
        className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[80vh] overflow-hidden animate-fade-in"
      >
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-bold text-gray-800">Search Articles</h3>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700 transition-colors"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          <div className="flex items-center gap-2">
            <div className="relative flex-1">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Search articles..."
                className="w-full px-4 py-2 pr-10 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                autoFocus
              />
              <Search className="absolute right-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            </div>
            <button
              onClick={() => handleSearch(searchQuery)}
              className="px-4 py-2 bg-blue-900 text-white rounded-lg hover:bg-blue-800 transition-colors"
            >
              Search
            </button>
          </div>
        </div>

        <div className="overflow-y-auto p-4" style={{ maxHeight: 'calc(80vh - 140px)' }}>
          {error && (
            <div className="mb-4 p-4 bg-red-50 text-red-700 rounded-lg">
              {error}
            </div>
          )}

          {loading ? (
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="bg-white p-4 rounded-lg shadow animate-pulse">
                  <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
                  <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                </div>
              ))}
            </div>
          ) : articles.length > 0 ? (
            <div className="space-y-4">
              {articles.map((article) => (
                <NewsCard
                  key={article.id}
                  article={article}
                  onSave={onSaveArticle}
                  onShare={onShareArticle}
                />
              ))}
            </div>
          ) : searchQuery ? (
            <div className="text-center py-8 text-gray-500">
              No articles found for "{searchQuery}"
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
};

export default SearchModal; 