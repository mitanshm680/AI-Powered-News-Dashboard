import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface Article {
  id: string;
  title: string;
  summary: string;
  category: string;
  source: string;
  imageUrl?: string;
  fullArticleUrl: string;
  publishedAt: string;
  saved: boolean;
  viewCount: number;
  readTimeMinutes?: number;
}

export interface ArticleList {
  articles: Article[];
  totalCount: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

export interface Category {
  name: string;
  count: number;
}

export const articlesApi = {
  getArticles: async (params: {
    page?: number;
    pageSize?: number;
    category?: string;
    source?: string;
    savedOnly?: boolean;
    sortBy?: string;
    sortOrder?: 'asc' | 'desc';
  }) => {
    const { data } = await api.get<ArticleList>('/articles', { params });
    return data;
  },

  getArticleById: async (id: string) => {
    const { data } = await api.get(`/article/${id}`);
    return data;
  },

  toggleSaveArticle: async (id: string, saved: boolean) => {
    const { data } = await api.post(`/article/${id}/save`, { saved });
    return data;
  },

  getCategories: async () => {
    const { data } = await api.get<{ data: Category[] }>('/categories');
    return data.data;
  },

  getTrendingArticles: async (params: { days?: number; limit?: number }) => {
    const { data } = await api.get<Article[]>('/articles/trending', { params });
    return data;
  },

  getLatestArticles: async (params: {
    limit?: number;
    category?: string;
    source?: string;
  }) => {
    const { data } = await api.get<Article[]>('/articles/latest', { params });
    return data;
  },
};

export default api; 