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
      <div className="p-4">
        <div className="flex flex-wrap gap-2">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="animate-pulse bg-gray-200 h-8 w-24 rounded-full"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="p-4">
      <div className="flex flex-wrap gap-2">
        {categories.map((category) => (
          <button
            key={category.name}
            onClick={() => onSelectCategory(category.name)}
            className={`
              px-4 py-2 rounded-full text-sm font-medium transition-all duration-200
              ${selectedCategory === category.name
                ? 'bg-blue-600 text-white shadow-md hover:bg-blue-700'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }
            `}
          >
            {category.name.charAt(0).toUpperCase() + category.name.slice(1)}
            <span className="ml-2 text-xs opacity-75">
              ({category.count})
            </span>
          </button>
        ))}
      </div>
    </div>
  );
};

export default CategorySelector;