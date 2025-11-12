# Find My Angel - Frontend

React + TypeScript application for searching and displaying business angel profiles.

## Features

- **TypeScript** for type safety and better developer experience
- **Vite** for fast development and building
- **Multiline Search Box** with voice input support (Web Speech API)
- **Advanced Filters** for refining search results
- **Grid Layout** displaying results in compact cards
- **Modal View** for full profile details
- **Clickable LinkedIn URLs** that open in new tabs

## Setup

1. Install dependencies:
```bash
npm install
```

2. Set the API URL (optional, defaults to http://localhost:8000):
```bash
# Create .env file
echo "VITE_API_URL=http://localhost:8000" > .env
```

3. Start the development server:
```bash
npm run dev
```

The app will open at http://localhost:3000

## Build for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## Preview Production Build

```bash
npm run preview
```

## Usage

1. Enter your search query in the search box
2. Use Ctrl/Cmd + Enter to search, or click the search button
3. Click the filter icon to refine your search
4. Click on any profile card to view full details in a modal
5. Click LinkedIn links to open profiles in a new tab

## Voice Input

Voice input uses the Web Speech API and works best in Chrome or Edge browsers. Click the microphone icon to start/stop voice input.

## API Integration

The frontend expects the FastAPI server to be running on port 8000 (or the URL specified in `VITE_API_URL`).

Make sure the backend server is running before using the frontend.

## Technology Stack

- **React 18.3** - UI library
- **TypeScript 5.5** - Type safety
- **Vite 5.4** - Build tool and dev server
- **Axios 1.7** - HTTP client

