# Static Files Directory

This directory contains built frontend assets and static files for the Bike-Dream application.

## Contents:
- CSS files (compiled from Tailwind)
- JavaScript bundles (React build output)
- Images and media files
- Favicon and other static assets

## Development vs Production:
- **Development**: Frontend runs on separate React dev server (port 3000)
- **Production**: Built frontend files are served from this directory by the FastAPI backend

## Build Process:
To build frontend for production:
```bash
cd frontend
npm run build
cp -r build/* ../static/
```