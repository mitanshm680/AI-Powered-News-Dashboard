import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import CategorySelector from './components/CategorySelector';
import NewsFeed from './components/NewsFeed';
import ShareModal from './components/ShareModal';
import { useArticles } from './hooks/useArticles';
import { Article } from './services/api';

function App() {
  const {
    articles,
    savedArticles,
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
  const [showSavedArticles, setShowSavedArticles] = useState(false);
  
  // Initialize dark mode from localStorage or system preference
  const [isDarkMode, setIsDarkMode] = useState(() => {
    if (typeof window !== 'undefined') {
      // First check localStorage
      const savedMode = localStorage.getItem('darkMode');
      if (savedMode !== null) {
        // Apply dark mode class immediately if saved preference exists
        if (JSON.parse(savedMode)) {
          document.documentElement.classList.add('dark');
        } else {
          document.documentElement.classList.remove('dark');
        }
        return JSON.parse(savedMode);
      }
      // If not in localStorage, check system preference
      const systemPreference = window.matchMedia('(prefers-color-scheme: dark)').matches;
      // Apply dark mode class immediately based on system preference
      if (systemPreference) {
        document.documentElement.classList.add('dark');
      }
      return systemPreference;
    }
    return false;
  });

  // Listen for system color scheme changes
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = (e: MediaQueryListEvent) => {
      if (localStorage.getItem('darkMode') === null) {
        setIsDarkMode(e.matches);
      }
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  // Apply dark mode class and update localStorage when isDarkMode changes
  useEffect(() => {
    const root = document.documentElement;
    if (isDarkMode) {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
    localStorage.setItem('darkMode', JSON.stringify(isDarkMode));
  }, [isDarkMode]);

  const handleShareArticle = (article: Article) => {
    setShareArticle(article);
  };

  const closeShareModal = () => {
    setShareArticle(null);
  };

  const handleShowSavedArticles = () => {
    setShowSavedArticles(true);
    setSelectedCategory('all'); // Reset category selection when viewing saved articles
  };

  const handleToggleDarkMode = () => {
    setIsDarkMode((prev: boolean) => !prev);
  };

  // Determine which articles to display
  const displayedArticles = showSavedArticles ? savedArticles : articles;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
      <Header 
        onSaveArticle={handleSaveArticle}
        onShareArticle={handleShareArticle}
        onShowSavedArticles={handleShowSavedArticles}
        isDarkMode={isDarkMode}
        onToggleDarkMode={handleToggleDarkMode}
      />
      
      <main className="container mx-auto px-4 py-6">
        {!showSavedArticles && (
          <div className="mb-6 bg-white dark:bg-gray-800 rounded-lg shadow-sm">
            <CategorySelector
              selectedCategory={selectedCategory}
              onSelectCategory={(category) => {
                setSelectedCategory(category);
                setShowSavedArticles(false);
              }}
            />
          </div>
        )}

        {showSavedArticles && (
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-gray-800 dark:text-white">
              Saved Articles
            </h2>
            <button
              onClick={() => setShowSavedArticles(false)}
              className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
            >
              ← Back to all articles
            </button>
          </div>
        )}
        
        {error && (
          <div className="my-4 p-4 bg-red-50 dark:bg-red-900 text-red-700 dark:text-red-100 rounded-lg">
            {error}
          </div>
        )}

        <NewsFeed
          articles={displayedArticles}
          onSaveArticle={handleSaveArticle}
          onShareArticle={handleShareArticle}
          loading={loading}
          hasMore={!showSavedArticles && hasMore}
          onLoadMore={loadMore}
          totalCount={showSavedArticles ? savedArticles.length : totalCount}
        />
      </main>

      {shareArticle && (
        <ShareModal article={shareArticle} onClose={closeShareModal} />
      )}
    </div>
  );
}

export default App;