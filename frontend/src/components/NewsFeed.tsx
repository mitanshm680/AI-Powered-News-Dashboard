import React from 'react';
import { Article } from '../types';
import NewsCard from './NewsCard';

interface NewsFeedProps {
  articles: Article[];
  onSaveArticle: (id: string) => void;
  onShareArticle: (article: Article) => void;
}

const NewsFeed: React.FC<NewsFeedProps> = ({ 
  articles, 
  onSaveArticle, 
  onShareArticle 
}) => {
  if (articles.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 px-4">
        <p className="text-gray-500 text-lg">No articles found in this category.</p>
      </div>
    );
  }

  return (
    <div className="pb-6">
      {articles.map((article) => (
        <div key={article.id} className="px-4 py-2">
          <NewsCard
            article={article}
            onSave={onSaveArticle}
            onShare={onShareArticle}
          />
        </div>
      ))}
    </div>
  );
};

export default NewsFeed;