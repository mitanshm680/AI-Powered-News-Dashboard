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

export interface Category {
  name: string;
  count: number;
}

export interface ArticleList {
  articles: Article[];
  totalCount: number;
  page: number;
  pageSize: number;
  totalPages: number;
}