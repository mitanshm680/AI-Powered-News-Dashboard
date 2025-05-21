import React, { useState, useRef, useEffect } from 'react';
import { Newspaper, Search, Settings, Bookmark, Moon, Sun } from 'lucide-react';
import SearchModal from './SearchModal';
import { Article } from '../services/api';

interface HeaderProps {
  onSaveArticle: (id: string) => void;
  onShareArticle: (article: Article) => void;
  onShowSavedArticles: () => void;
  isDarkMode: boolean;
  onToggleDarkMode: () => void;
}

const Header: React.FC<HeaderProps> = ({
  onSaveArticle,
  onShareArticle,
  onShowSavedArticles,
  isDarkMode,
  onToggleDarkMode
}) => {
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const settingsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (settingsRef.current && !settingsRef.current.contains(event.target as Node)) {
        setIsSettingsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  return (
    <header className="sticky top-0 bg-white dark:bg-gray-800 shadow-sm z-20">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-2">
            <Newspaper className="h-6 w-6 text-blue-600" />
            <span className="text-xl font-bold text-gray-800 dark:text-white">SmartBrief</span>
          </div>

          <div className="flex items-center space-x-4">
            <button
              onClick={() => setIsSearchOpen(true)}
              className="p-2 text-gray-600 hover:text-blue-600 dark:text-gray-300 dark:hover:text-blue-500 transition-colors"
              title="Search articles"
            >
              <Search className="h-5 w-5" />
            </button>

            <div className="relative" ref={settingsRef}>
              <button
                onClick={() => setIsSettingsOpen(!isSettingsOpen)}
                className="p-2 text-gray-600 hover:text-blue-600 dark:text-gray-300 dark:hover:text-blue-500 transition-colors"
                title="Settings"
              >
                <Settings className="h-5 w-5" />
              </button>

              {isSettingsOpen && (
                <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-700 rounded-lg shadow-lg py-1 z-30">
                  <button
                    onClick={() => {
                      onShowSavedArticles();
                      setIsSettingsOpen(false);
                    }}
                    className="flex items-center w-full px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-600"
                  >
                    <Bookmark className="h-4 w-4 mr-2" />
                    Saved Articles
                  </button>
                  <button
                    onClick={() => {
                      onToggleDarkMode();
                      setIsSettingsOpen(false);
                    }}
                    className="flex items-center w-full px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-600"
                  >
                    {isDarkMode ? (
                      <Sun className="h-4 w-4 mr-2" />
                    ) : (
                      <Moon className="h-4 w-4 mr-2" />
                    )}
                    {isDarkMode ? 'Light Mode' : 'Dark Mode'}
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {isSearchOpen && (
        <SearchModal
          onClose={() => setIsSearchOpen(false)}
          onSaveArticle={onSaveArticle}
          onShareArticle={onShareArticle}
        />
      )}
    </header>
  );
};

export default Header;