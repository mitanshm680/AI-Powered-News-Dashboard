import React, { useEffect, useRef, useCallback } from 'react';
import { Article } from '../types';
import NewsCard from './NewsCard';
import { sortArticlesByDate } from '../utils/sorting';

interface NewsFeedProps {
  articles: Article[];
  onSaveArticle: (id: string) => void;
  onShareArticle: (article: Article) => void;
  loading?: boolean;
  hasMore?: boolean;
  onLoadMore?: () => void;
  totalCount?: number;
}

const NewsFeed: React.FC<NewsFeedProps> = ({ 
  articles, 
  onSaveArticle, 
  onShareArticle,
  loading,
  hasMore,
  onLoadMore,
  totalCount = 0
}) => {
  const observer = useRef<IntersectionObserver | null>(null);
  const loadMoreRef = useRef<HTMLDivElement>(null);

  const handleObserver = useCallback((entries: IntersectionObserverEntry[]) => {
    const target = entries[0];
    if (target.isIntersecting && hasMore && !loading) {
      onLoadMore?.();
    }
  }, [hasMore, loading, onLoadMore]);

  useEffect(() => {
    const options = {
      root: null,
      rootMargin: '20px',
      threshold: 1.0
    };

    observer.current = new IntersectionObserver(handleObserver, options);

    if (loadMoreRef.current) {
      observer.current.observe(loadMoreRef.current);
    }

    return () => {
      if (observer.current) {
        observer.current.disconnect();
      }
    };
  }, [handleObserver]);

  if (articles.length === 0 && !loading) {
    return (
      <div className="flex flex-col items-center justify-center py-12 px-4">
        <p className="text-gray-500 text-lg">No articles found in this category.</p>
      </div>
    );
  }

  const sortedArticles = sortArticlesByDate(articles);

  return (
    <>
      {totalCount > 0 && (
        <div className="text-gray-600 mb-4">
          Showing {articles.length} of {totalCount} articles
        </div>
      )}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {sortedArticles.map((article) => (
          <div key={article.id}>
            <NewsCard
              article={article}
              onSave={onSaveArticle}
              onShare={onShareArticle}
            />
          </div>
        ))}
      </div>
      {loading && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-6">
          {[1, 2, 3].map((i) => (
            <div key={i} className="bg-white p-4 rounded-lg shadow animate-pulse">
              <div className="h-48 bg-gray-200 rounded mb-4"></div>
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
              <div className="h-4 bg-gray-200 rounded w-1/2"></div>
            </div>
          ))}
        </div>
      )}
      {hasMore && <div ref={loadMoreRef} className="h-10" />}
    </>
  );
};

export default NewsFeed;