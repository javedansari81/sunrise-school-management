# Sunrise School Frontend

A modern React-based frontend for the Sunrise School Management System built with TypeScript and Material-UI.

## Quick Start

### Prerequisites
- Node.js 16+
- npm or yarn

### Installation

1. **Navigate to the frontend directory:**
```bash
cd sunrise-school-frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Start the development server:**
```bash
npm start
```

The frontend will be available at `http://localhost:3000`

## Project Structure

```
sunrise-school-frontend/
├── src/                    # Main application code
│   ├── components/         # Reusable React components
│   ├── pages/             # Page components and routes
│   ├── contexts/          # React contexts for state management
│   ├── services/          # API services and utilities
│   ├── hooks/             # Custom React hooks
│   └── App.tsx            # Main application component
├── src/                    # Main application code (tests moved to workspace root)
├── docs/                  # Documentation files
├── public/                # Static assets
├── build/                 # Production build output
└── package.json           # Dependencies and scripts
```

## Available Scripts

- **`npm start`** - Start development server
- **`npm test`** - Run test suite
- **`npm run build`** - Build for production
- **`npm run eject`** - Eject from Create React App (one-way operation)

## Testing

Run all tests:
```bash
npm test
```

Run tests in watch mode:
```bash
npm test -- --watch
```

Run tests with coverage:
```bash
npm test -- --coverage
```

## Documentation

For detailed documentation, setup instructions, and technical details, see the [docs/](./docs/) folder:

- **[Complete Setup Guide](./docs/README.md)** - Detailed installation and configuration
- **[Metadata-Driven UI Changes](./docs/METADATA_DRIVEN_UI_CHANGES.md)** - UI architecture details

## Features

- **React 19** - Latest React with modern features
- **TypeScript** - Type-safe development
- **Material-UI v7** - Modern component library
- **React Router** - Client-side routing
- **Axios** - HTTP client for API calls
- **Date-fns** - Modern date utility library
- **Comprehensive Testing** - Jest and React Testing Library

## Environment Variables

Create a `.env` file in the root directory:

```env
REACT_APP_API_URL=http://localhost:8000/api/v1
REACT_APP_SCHOOL_NAME=Sunrise National Public School
```

## Build and Deployment

Build for production:
```bash
npm run build
```

The build artifacts will be stored in the `build/` directory.

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
