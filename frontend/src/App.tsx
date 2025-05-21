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
      
      <main className="container mx-auto max-w-2xl px-4">
        <CategorySelector
          selectedCategory={selectedCategory}
          onSelectCategory={setSelectedCategory}
        />
        
        {error && (
          <div className="my-4 p-4 bg-red-50 text-red-700 rounded-lg">
            {error}
          </div>
        )}

        {loading ? (
          <div className="space-y-4 mt-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="bg-white p-4 rounded-lg shadow animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
                <div className="h-4 bg-gray-200 rounded w-1/2"></div>
              </div>
            ))}
          </div>
        ) : (
          <NewsFeed
            articles={articles}
            onSaveArticle={handleSaveArticle}
            onShareArticle={handleShareArticle}
          />
        )}
      </main>

      {shareArticle && (
        <ShareModal article={shareArticle} onClose={closeShareModal} />
      )}
    </div>
  );
}

export default App;