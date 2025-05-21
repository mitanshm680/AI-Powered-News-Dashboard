import { useState, useEffect, useCallback } from 'react';
import { articlesApi, Article } from '../services/api';
import { sortArticlesByDate } from '../utils/sorting';

export const useArticles = () => {
  const [articles, setArticles] = useState<Article[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [totalCount, setTotalCount] = useState(0);

  const fetchArticles = useCallback(async (pageNum: number) => {
    try {
      setLoading(true);
      setError(null);
      const response = await articlesApi.getArticles({
        category: selectedCategory === 'all' ? undefined : selectedCategory,
        page: pageNum,
        pageSize: 30,
        sortBy: 'publishedAt',
        sortOrder: 'desc',
      });

      if (pageNum === 1) {
        setArticles(response.articles);
      } else {
        setArticles(prev => [...prev, ...response.articles]);
      }

      setTotalCount(response.totalCount);
      setHasMore(pageNum < response.totalPages);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch articles');
    } finally {
      setLoading(false);
    }
  }, [selectedCategory]);

  // Reset pagination when category changes
  useEffect(() => {
    setPage(1);
    setHasMore(true);
    fetchArticles(1);
  }, [selectedCategory, fetchArticles]);

  const loadMore = async () => {
    if (!loading && hasMore) {
      const nextPage = page + 1;
      setPage(nextPage);
      await fetchArticles(nextPage);
    }
  };

  const handleSaveArticle = async (id: string) => {
    try {
      const article = articles.find(a => a.id === id);
      if (!article) return;

      await articlesApi.toggleSaveArticle(id, !article.saved);
      setArticles(prevArticles =>
        sortArticlesByDate(
          prevArticles.map(article =>
            article.id === id
              ? { ...article, saved: !article.saved }
              : article
          )
        )
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save article');
    }
  };

  const getSavedArticles = () => {
    return sortArticlesByDate(articles.filter(article => article.saved));
  };

  return {
    articles,
    savedArticles: getSavedArticles(),
    selectedCategory,
    setSelectedCategory,
    handleSaveArticle,
    loading,
    error,
    loadMore,
    hasMore,
    totalCount,
    refetch: () => fetchArticles(1),
  };
};