# Static Images Directory

This directory contains placeholder and fallback images for the Bike-Dream application.

## Default Motorcycle Placeholder

The default motorcycle placeholder is used when:
- No image URL is provided
- External image URLs fail to load
- API requests for dynamic images fail

## Image Optimization Strategy

1. **Primary**: Try to load authentic motorcycle images from database
2. **Secondary**: Use manufacturer-specific fallback images
3. **Tertiary**: Use category-specific fallback images  
4. **Final**: Use default placeholder

## Supported Image Formats
- JPEG/JPG (preferred for photos)
- PNG (for images with transparency)
- WebP (for modern browsers)
- SVG (for icons and simple graphics)

## Performance Considerations
- All images are optimized with query parameters: `?w=400&h=250&fit=crop&auto=format&q=80`
- Lazy loading implemented for better performance
- CrossOrigin="anonymous" for CORS compatibility