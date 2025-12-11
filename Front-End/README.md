# OmniA Front-End

Modern React + TypeScript frontend for the OmniA personal archive system.

## Features

- 🔐 **Login Page** - Secure authentication
- 📦 **Archive Management** - Browse, search, and add items
- 🤖 **AI Agent** - Query your archive with natural language
- 🗺️ **Map View** - Visualize items with location data
- 🎨 **Modern UI** - Built with Tailwind CSS
- ⚡ **Fast** - Powered by Vite

## Tech Stack

- **React 18** with TypeScript
- **Vite** for lightning-fast development
- **Tailwind CSS** for styling
- **React Router** for navigation
- **Zustand** for state management
- **Axios** for API calls
- **React Leaflet** for maps
- **Lucide React** for icons

## Getting Started

### Install Dependencies

```bash
npm install
```

### Development Server

```bash
npm run dev
```

The app will be available at http://localhost:3000

### Build for Production

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── Layout.tsx      # Main layout with sidebar
│   ├── ArchiveItemCard.tsx
│   └── CreateArchiveModal.tsx
├── pages/              # Page components
│   ├── LoginPage.tsx   # Authentication
│   ├── ArchivePage.tsx # Archive management
│   ├── AgentPage.tsx   # AI query interface
│   └── MapPage.tsx     # Map visualization
├── store/              # State management
│   └── authStore.ts    # Authentication state
├── lib/                # Utilities
│   └── api.ts          # Axios instance
├── types/              # TypeScript types
│   └── index.ts
├── App.tsx             # Root component with routing
├── main.tsx            # Entry point
└── index.css           # Global styles
```

## API Integration

The frontend connects to the backend API Gateway at `http://localhost:8000` (proxied through Vite).

### Key Endpoints

- `POST /api/auth/login` - User authentication
- `GET /api/v1/archive/items` - List archive items
- `POST /api/v1/archive/text` - Create text archive
- `POST /api/v1/archive/file` - Upload file
- `POST /api/v1/archive/instagram` - Add Instagram link
- `GET /api/v1/archive/map/all` - Get map markers
- `POST /api/v1/query` - Query AI agent

## Features

### Archive Management

- Create items with text, files, or Instagram URLs
- Automatic location extraction from text content
- Search and filter by field and tags
- View item details with location data

### AI Agent

- Natural language queries about your archive
- Field-specific filtering
- Conversation history
- Suggested prompts

### Map View

- Interactive map with OpenStreetMap tiles
- Color-coded markers by field
- Filter by field
- Popup with item details
- Auto-centering on markers

## Environment Variables

Create a `.env` file if needed:

```env
VITE_API_URL=http://localhost:8000
```

## Development Tips

### Hot Reload

Vite provides instant hot module replacement (HMR). Changes are reflected immediately.

### Type Checking

```bash
npm run lint
```

### Debugging

Open browser DevTools (F12) to inspect API calls, console logs, and errors.

## Deployment

### Docker

```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Nginx Configuration

```nginx
server {
  listen 80;
  location / {
    root /usr/share/nginx/html;
    try_files $uri /index.html;
  }
  location /api {
    proxy_pass http://api-gateway:8000;
  }
}
```

## Browser Support

- Chrome/Edge (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)

## License

MIT
