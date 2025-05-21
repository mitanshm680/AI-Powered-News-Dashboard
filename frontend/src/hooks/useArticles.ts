import { useState, useEffect } from 'react';
import { articlesApi, Article } from '../services/api';

export const useArticles = () => {
  const [articles, setArticles] = useState<Article[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchArticles = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await articlesApi.getArticles({
        category: selectedCategory === 'all' ? undefined : selectedCategory,
        pageSize: 20,
        sortBy: 'publishedAt',
        sortOrder: 'desc',
      });
      setArticles(response.articles);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch articles');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchArticles();
  }, [selectedCategory]);

  const handleSaveArticle = async (id: string) => {
    try {
      const article = articles.find(a => a.id === id);
      if (!article) return;

      await articlesApi.toggleSaveArticle(id, !article.saved);
      setArticles(prevArticles =>
        prevArticles.map(article =>
          article.id === id
            ? { ...article, saved: !article.saved }
            : article
        )
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save article');
    }
  };

  const getSavedArticles = () => {
    return articles.filter(article => article.saved);
  };

  return {
    articles,
    savedArticles: getSavedArticles(),
    selectedCategory,
    setSelectedCategory,
    handleSaveArticle,
    loading,
    error,
    refetch: fetchArticles,
  };
};