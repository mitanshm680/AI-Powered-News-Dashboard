import React, { useState } from 'react';
import { Newspaper, Search, Settings } from 'lucide-react';
import SearchModal from './SearchModal';
import { Article } from '../services/api';

interface HeaderProps {
  onSaveArticle: (id: string) => void;
  onShareArticle: (article: Article) => void;
}

const Header: React.FC<HeaderProps> = ({ onSaveArticle, onShareArticle }) => {
  const [isSearchOpen, setIsSearchOpen] = useState(false);

  return (
    <>
      <header className="sticky top-0 z-10 bg-white border-b border-gray-200">
        <div className="container mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <Newspaper className="h-6 w-6 text-blue-900" />
              <h1 className="ml-2 text-xl font-bold text-blue-900">SmartBrief</h1>
            </div>
            
            <div className="flex items-center space-x-4">
              <button
                className="p-2 text-gray-600 hover:text-blue-900 transition-colors"
                aria-label="Search"
                onClick={() => setIsSearchOpen(true)}
              >
                <Search className="h-5 w-5" />
              </button>
              <button
                className="p-2 text-gray-600 hover:text-blue-900 transition-colors"
                aria-label="Settings"
              >
                <Settings className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {isSearchOpen && (
        <SearchModal
          onClose={() => setIsSearchOpen(false)}
          onSaveArticle={onSaveArticle}
          onShareArticle={onShareArticle}
        />
      )}
    </>
  );
};

export default Header;