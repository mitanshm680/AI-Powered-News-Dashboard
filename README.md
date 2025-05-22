# SmartBrief - AI Powered News Dashboard

A full-stack web application that automatically collects, summarizes, and categorizes news articles from multiple sources. The application features a responsive React frontend, a Python backend with FastAPI, and uses MongoDB as the database for efficient storage and retrieval of news articles.

## Features

- **Automated News Collection**: Scrapes news articles from multiple configurable sources
- **Smart Summarization**: Uses Google's Gemini 2.0 API to generate concise article summaries
- **Article Management**: Save, filter, and search articles by category or source
- **Responsive UI**: Dark/light mode, mobile-friendly interface built with React and Tailwind CSS
- **Scheduled Updates**: Automatically fetches and processes news at regular intervals

## Project Structure

```
news_summary_dashboard/
├── frontend/                       # React frontend application
│   ├── node_modules/               # Frontend dependencies
│   ├── public/                     # Public static assets
│   │   └── 1.png                   # Sample image asset
│   ├── src/                        # Frontend source code
│   │   ├── components/             # React components
│   │   │   ├── Header.tsx          # App header component
│   │   │   ├── NewsCard.tsx        # News article card component
│   │   │   ├── ArticleModal.tsx    # Article detail modal
│   │   │   ├── NewsFeed.tsx        # Container for news cards
│   │   │   ├── CategorySelector.tsx # Category filter component
│   │   │   ├── SearchModal.tsx     # Search interface modal
│   │   │   └── ShareModal.tsx      # Article sharing modal
│   │   ├── services/               # API services
│   │   │   └── api.ts              # API client configuration
│   │   ├── hooks/                  # Custom React hooks
│   │   │   └── useArticles.ts      # Hook for article data management
│   │   ├── utils/                  # Utility functions
│   │   │   ├── dateUtils.ts        # Date formatting utilities
│   │   │   └── sorting.ts          # Sorting helper functions
│   │   ├── types/                  # TypeScript type definitions
│   │   │   └── index.ts            # Type declarations
│   │   ├── data/                   # Mock data for development
│   │   │   ├── mockData.ts         # Mock data in TypeScript
│   │   │   └── mockData.json       # Mock data in JSON format
│   │   ├── App.tsx                 # Main application component
│   │   ├── main.tsx                # Application entry point
│   │   ├── vite-env.d.ts           # Vite environment types
│   │   └── index.css               # Global CSS styles
│   ├── package.json                # Frontend dependencies and scripts
│   ├── package-lock.json           # Locked dependency versions
│   ├── tsconfig.json               # TypeScript configuration
│   ├── tsconfig.app.json           # App-specific TypeScript config
│   ├── tsconfig.node.json          # Node TypeScript config
│   ├── vite.config.ts              # Vite bundler configuration
│   ├── tailwind.config.js          # Tailwind CSS configuration
│   ├── postcss.config.js           # PostCSS configuration
│   ├── eslint.config.js            # ESLint configuration
│   └── .gitignore                  # Git ignore rules
│
├── backend/                        # Python backend application
│   ├── api.py                      # FastAPI REST endpoints
│   ├── db.py                       # MongoDB database operations
│   ├── scraper.py                  # News article scraper
│   ├── summarizer.py               # Text summarization with Gemini API
│   ├── fetch_and_store.py          # Article fetching and storage logic
│   ├── scheduler.py                # Scheduled task manager
│   ├── scheduler_status.json       # Scheduler configuration and status
│   ├── main.py                     # Main CLI entry point
│   ├── models.py                   # Data models
│   ├── ratelimit_test.py           # API rate limiting test
│   ├── requirements.txt            # Python dependencies
│   ├── api.log                     # API server logs
│   ├── scheduler.log               # Scheduler logs
│   ├── news_fetcher.log            # News fetching logs
│   ├── mongodb_data/               # Local MongoDB data files
│   └── venv/                       # Python virtual environment
│
├── .git/                           # Git repository data
├── .gitignore                      # Git ignore rules
├── README.md                       # Project documentation (this file)
├── scheduler.log                   # Root-level scheduler logs
└── news_fetcher.log                # Root-level news fetcher logs
```

## Prerequisites

- Node.js (v14+) and npm for the frontend
- Python 3.8+ for the backend
- MongoDB database (local or cloud)
- Google Gemini API key (for advanced summarization)

## Environment Setup

### Backend Environment Variables

Create a `.env` file in the `backend` directory with the following variables:

```
MONGODB_URI=mongodb://localhost:27017/news_dashboard
GEMINI_API_KEY=your_gemini_api_key_here
API_KEY=optional_api_key_for_securing_endpoints
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:5174
```

### Frontend Environment

The frontend connects to the backend API at `http://localhost:8000/api/v1` by default. If you need to change this, edit `frontend/src/services/api.ts`.

## Installation and Setup

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   pip install fastapi uvicorn
   ```

4. Start the backend API server:
   ```
   uvicorn api:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm run dev
   ```

4. Open your browser and navigate to `http://localhost:5173`

## Running the Application

### Using the Command Line Interface

The backend includes a command-line interface with several useful commands:

```
python main.py [command] [options]
```

Available commands:

- `test`: Test the scraper functionality
  ```
  python main.py test --source [source_name]
  ```

- `fetch`: Run a manual fetch job
  ```
  python main.py fetch
  ```

- `schedule`: Run the scheduler (continuous mode)
  ```
  python main.py schedule
  ```

- `stats`: Display database statistics
  ```
  python main.py stats
  ```

- `cleanup`: Clean up old articles
  ```
  python main.py cleanup --days 30
  ```

### Running the Scheduler

To keep the news articles updated automatically, run the scheduler:

```
python main.py schedule
```

This will start a background process that periodically fetches and processes news articles according to the configured schedule.

## API Documentation

When the backend is running, access the API documentation at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Development

### Adding a New News Source

To add a new news source, edit the `SOURCES` dictionary in `backend/scraper.py` with the appropriate configuration.

### Customizing the Summarization

The summarization logic is in `backend/summarizer.py`. You can adjust the prompt used for Gemini API or modify the fallback summarization logic.

## Building for Production

### Frontend

To build the frontend for production:

```
cd frontend
npm run build
```

The build output will be in the `frontend/dist` directory.

### Backend

For production deployment, consider using Gunicorn with Uvicorn workers:

```
pip install gunicorn
gunicorn -k uvicorn.workers.UvicornWorker -w 4 api:app
```

## Troubleshooting

- Check the log files (`api.log`, `scheduler.log`, `news_fetcher.log`) for any error messages
- Ensure MongoDB is running and accessible
- Verify your Gemini API key is correctly set in the `.env` file

## License

This project is open-source, free to use and modify. 