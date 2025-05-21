import React, { useEffect, useState } from 'react';
import { Category, articlesApi } from '../services/api';

interface CategorySelectorProps {
  selectedCategory: string;
  onSelectCategory: (category: string) => void;
}

const CategorySelector: React.FC<CategorySelectorProps> = ({
  selectedCategory,
  onSelectCategory,
}) => {
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        setLoading(true);
        const data = await articlesApi.getCategories();
        // Add 'all' category and sort others alphabetically
        const sortedCategories = [
          { name: 'all', count: data.reduce((sum, cat) => sum + cat.count, 0) },
          ...data.sort((a, b) => a.name.localeCompare(b.name))
        ];
        setCategories(sortedCategories);
      } catch (error) {
        console.error('Failed to fetch categories:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchCategories();
  }, []);

  if (loading) {
    return (
      <div className="overflow-x-auto scrollbar-hide">
        <div className="flex space-x-2 py-3 px-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="animate-pulse bg-gray-200 h-8 w-24 rounded-full"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="sticky top-16 bg-gray-50 z-10 border-b border-gray-200">
      <div className="overflow-x-auto scrollbar-hide">
        <div className="flex space-x-2 py-3 px-4">
          {categories.map((category) => (
            <button
              key={category.name}
              onClick={() => onSelectCategory(category.name)}
              className={`
                px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-all
                ${selectedCategory === category.name
                  ? 'bg-blue-900 text-white shadow-lg transform scale-105'
                  : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-200'
                }
              `}
            >
              <span className="capitalize">{category.name}</span>
              <span className="ml-2 text-xs opacity-75">({category.count})</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default CategorySelector;