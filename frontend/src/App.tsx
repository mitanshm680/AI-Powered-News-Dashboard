import React, { useState } from 'react';
import Header from './components/Header';
import CategorySelector from './components/CategorySelector';
import NewsFeed from './components/NewsFeed';
import ShareModal from './components/ShareModal';
import { useArticles } from './hooks/useArticles';
import { Article } from './services/api';

function App() {
  const {
    articles,
    selectedCategory,
    setSelectedCategory,
    handleSaveArticle,
    loading,
    error,
    loadMore,
    hasMore,
    totalCount
  } = useArticles();

  const [shareArticle, setShareArticle] = useState<Article | null>(null);

  const handleShareArticle = (article: Article) => {
    setShareArticle(article);
  };

  const closeShareModal = () => {
    setShareArticle(null);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header 
        onSaveArticle={handleSaveArticle}
        onShareArticle={handleShareArticle}
      />
      
      <main className="container mx-auto px-4 py-6">
        <div className="mb-6 bg-white rounded-lg shadow-sm">
          <CategorySelector
            selectedCategory={selectedCategory}
            onSelectCategory={setSelectedCategory}
          />
        </div>
        
        {error && (
          <div className="my-4 p-4 bg-red-50 text-red-700 rounded-lg">
            {error}
          </div>
        )}

        <NewsFeed
          articles={articles}
          onSaveArticle={handleSaveArticle}
          onShareArticle={handleShareArticle}
          loading={loading}
          hasMore={hasMore}
          onLoadMore={loadMore}
          totalCount={totalCount}
        />
      </main>

      {shareArticle && (
        <ShareModal article={shareArticle} onClose={closeShareModal} />
      )}
    </div>
  );
}

export default App;