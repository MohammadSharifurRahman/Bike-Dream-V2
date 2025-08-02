# 🏍️ Bike-Dream: Comprehensive Motorcycle Database

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org)
[![MongoDB](https://img.shields.io/badge/MongoDB-4.5+-green.svg)](https://mongodb.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A comprehensive motorcycle database application featuring advanced search, filtering, comparison tools, and user management. Built with FastAPI backend, React frontend, and MongoDB database.

## 🌟 Key Features

- **📊 Comprehensive Database**: 5,060+ motorcycles from 1900 to present
- **🔍 Advanced Search**: Auto-complete suggestions with manufacturer and model filtering
- **🌍 Regional Filtering**: Country-specific availability and pricing (67+ countries)
- **⚖️ Motorcycle Comparison**: Side-by-side comparison of up to 3 motorcycles
- **👤 User Management**: Authentication, favorites, garage, and user roles
- **🏷️ Dynamic Pricing**: Multi-currency support with regional pricing
- **📱 Responsive Design**: Mobile-first design with Tailwind CSS
- **🔧 Admin Dashboard**: Content management and analytics

## 🏗️ Project Structure

```
bike-dream/
├── app.py                          # 🚀 Main entry point for production
├── requirements.txt                # 📦 Python dependencies
├── Procfile                       # 🌐 Deployment configuration
├── render.yaml                    # ☁️ Render.com deployment config
├── .env                          # 🔐 Environment variables (local)
├── .env.example                  # 📋 Environment template
├── README.md                     # 📖 This documentation
│
├── api/                          # 🔧 Backend API modules
│   ├── __init__.py              # Python module init
│   ├── server.py                # 🎯 FastAPI application & routes
│   ├── comprehensive_motorcycles.py  # 📊 Motorcycle data models
│   ├── vendor_pricing.py        # 💰 Pricing logic
│   └── daily_update_bot.py      # 🤖 Automated data updates
│
├── frontend/                     # ⚛️ React frontend (development)
│   ├── src/
│   │   ├── App.js               # 🎨 Main React component
│   │   ├── App.css              # 🎨 Custom styles
│   │   └── index.js             # ⚛️ React entry point
│   ├── public/                  # 📁 Public assets
│   ├── package.json             # 📦 Node.js dependencies
│   └── tailwind.config.js       # 🎨 Tailwind CSS configuration
│
├── static/                       # 📁 Built frontend assets (production)
├── templates/                    # 📄 HTML templates (future use)
├── tests/                        # 🧪 Test files
└── test_result.md               # 📋 Testing documentation
```

## 🛠️ Technology Stack

### Backend
- **FastAPI** (0.110+): Modern Python web framework
- **MongoDB** (4.5+): Document database with Motor async driver
- **Pydantic**: Data validation and serialization
- **JWT Authentication**: Secure user sessions
- **Uvicorn**: ASGI server for production

### Frontend
- **React** (18+): Component-based UI library
- **Tailwind CSS**: Utility-first CSS framework
- **Axios**: HTTP client for API calls
- **React Hooks**: Modern state management

### Database Schema
- **Motorcycles**: Main collection with 2,530+ documents
- **Users**: Authentication and user preferences
- **Reviews**: User ratings and comments
- **Analytics**: Search and engagement tracking

## 🚀 How the Application Works

### Backend Architecture
1. **FastAPI Server** (`api/server.py`):
   - Serves REST API endpoints under `/api/*` prefix
   - Handles authentication, CRUD operations, search, filtering
   - Connects to MongoDB using Motor (async MongoDB driver)
   - Provides real-time data with caching for performance

2. **Database Layer**:
   - MongoDB stores motorcycle data, user accounts, reviews
   - Advanced aggregation pipelines for filtering and statistics
   - Indexed fields for fast search and sorting

3. **Business Logic**:
   - Regional filtering by manufacturer availability
   - Dynamic pricing based on country/currency
   - Search suggestions with fuzzy matching
   - User authentication with JWT tokens

### Frontend Architecture
1. **React SPA** (`frontend/src/App.js`):
   - Single-page application with component-based architecture
   - State management using React Hooks
   - Responsive design with mobile-first approach

2. **API Integration**:
   - Frontend communicates with backend via REST APIs
   - All endpoints prefixed with `/api/` for proper routing
   - Error handling and loading states for better UX

3. **Key Components**:
   - **SearchBar**: Auto-complete with suggestions
   - **MotorcycleCard**: Display motorcycle information
   - **ComparisonTool**: Side-by-side motorcycle comparison
   - **FilterPanel**: Advanced filtering options
   - **UserDashboard**: Profile and garage management

### Data Flow
```
User Request → React Frontend → FastAPI Backend → MongoDB → Response Data → Frontend Rendering
```

## 📋 Requirements

- **Python**: 3.11 or higher
- **Node.js**: 16 or higher (for frontend development)
- **MongoDB**: 4.5 or higher
- **Memory**: 512MB RAM minimum
- **Storage**: 1GB disk space

## 🏃‍♂️ Local Development Setup

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd bike-dream
```

### 2. Backend Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your MongoDB URL
nano .env
```

### 3. Frontend Setup (Development)
```bash
cd frontend
npm install
```

### 4. Database Setup
```bash
# Start MongoDB (if local)
mongod

# The app will automatically create collections and seed data
```

### 5. Start Development Servers

**Option A: Start both servers separately**
```bash
# Terminal 1: Start backend
python app.py

# Terminal 2: Start frontend
cd frontend
npm start
```

**Option B: Using the integrated app.py**
```bash
# Start integrated server (backend + static frontend)
python app.py
```

### 6. Access the Application
- **Frontend**: http://localhost:3000 (development)
- **Backend API**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs

## 🚀 Production Deployment

### Deploy to Render.com

1. **Connect Repository**:
   - Fork this repository to your GitHub
   - Connect to Render.com

2. **Create Web Service**:
   - Choose "Web Service" from Render dashboard
   - Connect your GitHub repository
   - Use these settings:
     - **Environment**: Python 3.11
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `python app.py`

3. **Environment Variables**:
   Set these in Render dashboard:
   ```
   MONGO_URL=your-production-mongodb-url
   HOST=0.0.0.0
   PORT=8001
   DEBUG=false
   ```

4. **MongoDB Setup**:
   - Use MongoDB Atlas for production database
   - Whitelist Render.com IP addresses
   - Update MONGO_URL in environment variables

### Deploy to Other Platforms

**Heroku**:
```bash
heroku create your-app-name
heroku config:set MONGO_URL=your-mongodb-url
git push heroku main
```

**Railway**:
- Connect GitHub repository
- Set environment variables
- Railway will auto-deploy using Procfile

## 🧪 Testing

### Run Backend Tests
```bash
python -m pytest tests/ -v
```

### Manual Testing Checklist
- [ ] Homepage loads with motorcycle statistics
- [ ] Search functionality with auto-suggestions
- [ ] Region filtering updates counts and listings
- [ ] Motorcycle comparison (add/remove/compare)
- [ ] User registration and login
- [ ] Favorites and garage functionality
- [ ] Admin dashboard (if admin user)

### API Testing
```bash
# Test health endpoint
curl http://localhost:8001/api/stats

# Test search suggestions
curl "http://localhost:8001/api/motorcycles/search/suggestions?q=yamaha"
```

## 🤝 Contributing

### Adding New Features

1. **Backend Changes**:
   - Add new endpoints in `api/server.py`
   - Update database models if needed
   - Add corresponding tests

2. **Frontend Changes**:
   - Create new components in `frontend/src/`
   - Update `App.js` for routing/state
   - Ensure responsive design

3. **Database Changes**:
   - Update data models in `api/comprehensive_motorcycles.py`
   - Add migration scripts if needed

### Code Style
- **Python**: Follow PEP 8, use Black formatter
- **JavaScript**: Use Prettier, ESLint configuration
- **Commits**: Use conventional commit messages

### Pull Request Process
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `MONGO_URL` | MongoDB connection string | `mongodb://localhost:27017` | ✅ |
| `HOST` | Server host | `0.0.0.0` | ❌ |
| `PORT` | Server port | `8001` | ❌ |
| `DEBUG` | Debug mode | `false` | ❌ |
| `DB_NAME` | Database name | `bike_dream_db` | ❌ |

### Feature Flags
- Regional filtering: Always enabled
- User authentication: Always enabled
- Admin dashboard: Role-based access
- Comparison tool: Always enabled

## 📊 Performance Optimization

- **Database**: Indexed fields for fast queries
- **Caching**: In-memory caching for frequent queries
- **Images**: Optimized image loading with lazy loading
- **Frontend**: Code splitting and chunking
- **API**: Pagination for large datasets

## 🐛 Troubleshooting

### Common Issues

1. **MongoDB Connection Failed**:
   ```bash
   # Check MongoDB is running
   mongod --version
   
   # Verify connection string in .env
   echo $MONGO_URL
   ```

2. **Frontend Build Errors**:
   ```bash
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   ```

3. **Import Errors**:
   ```bash
   # Ensure all dependencies installed
   pip install -r requirements.txt
   ```

### Logs and Debugging
- **Backend Logs**: Check console output from `python app.py`
- **Frontend Logs**: Check browser console (F12)
- **Database Logs**: Check MongoDB logs
- **Production Logs**: Check Render/Heroku logs

## 📈 Analytics and Monitoring

The application includes built-in analytics:
- Search query tracking
- User engagement metrics
- Popular motorcycle tracking
- Regional usage statistics

## 🔐 Security

- JWT-based authentication
- Password hashing with bcrypt
- Input validation with Pydantic
- CORS configuration for cross-origin requests
- Environment variable protection

## 📞 Support

For issues and questions:
1. Check this README first
2. Search existing GitHub issues
3. Create new issue with detailed description
4. Include error logs and steps to reproduce

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FastAPI**: For the excellent web framework
- **React**: For the powerful frontend library
- **MongoDB**: For the flexible database
- **Tailwind CSS**: For the utility-first styling
- **Unsplash/Pexels**: For motorcycle images

---

**Built with ❤️ for motorcycle enthusiasts worldwide** 🏍️
