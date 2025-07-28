import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const MotorcycleCard = ({ motorcycle, onClick }) => (
  <div 
    className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 cursor-pointer transform hover:scale-105"
    onClick={() => onClick(motorcycle)}
  >
    <div className="relative">
      <img 
        src={motorcycle.image_url} 
        alt={`${motorcycle.manufacturer} ${motorcycle.model}`}
        className="w-full h-64 object-cover rounded-t-xl"
      />
      <div className="absolute top-4 right-4 bg-black bg-opacity-75 text-white px-3 py-1 rounded-full text-sm">
        {motorcycle.availability}
      </div>
      {motorcycle.user_interest_score > 90 && (
        <div className="absolute top-4 left-4 bg-red-500 text-white px-2 py-1 rounded-full text-xs font-bold">
          🔥 Popular
        </div>
      )}
    </div>
    <div className="p-6">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-xl font-bold text-gray-800">{motorcycle.manufacturer}</h3>
        <span className="text-sm bg-blue-100 text-blue-800 px-2 py-1 rounded-full">{motorcycle.category}</span>
      </div>
      <h4 className="text-lg text-gray-600 mb-3">{motorcycle.model}</h4>
      <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
        <span>{motorcycle.year}</span>
        <span>{motorcycle.displacement}cc</span>
        <span>{motorcycle.horsepower}hp</span>
      </div>
      <div className="flex items-center justify-between">
        <span className="text-2xl font-bold text-green-600">${motorcycle.price_usd.toLocaleString()}</span>
        <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
          View Details
        </button>
      </div>
    </div>
  </div>
);

const CategorySection = ({ category, onMotorcycleClick }) => (
  <div className="mb-12">
    <div className="flex items-center justify-between mb-6">
      <div>
        <h2 className="text-3xl font-bold text-gray-800">{category.category}</h2>
        <p className="text-gray-600">{category.count} motorcycles available</p>
      </div>
      <button className="text-blue-600 hover:text-blue-800 font-medium">
        View All {category.category} →
      </button>
    </div>
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {category.featured_motorcycles.map((motorcycle) => (
        <MotorcycleCard
          key={motorcycle.id}
          motorcycle={motorcycle}
          onClick={onMotorcycleClick}
        />
      ))}
    </div>
  </div>
);

const MotorcycleDetail = ({ motorcycle, onClose }) => (
  <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
    <div className="bg-white rounded-xl max-w-4xl w-full max-h-screen overflow-y-auto">
      <div className="relative">
        <img 
          src={motorcycle.image_url} 
          alt={`${motorcycle.manufacturer} ${motorcycle.model}`}
          className="w-full h-80 object-cover rounded-t-xl"
        />
        <button 
          onClick={onClose}
          className="absolute top-4 right-4 bg-black bg-opacity-50 text-white w-10 h-10 rounded-full flex items-center justify-center hover:bg-opacity-75"
        >
          ×
        </button>
        {motorcycle.user_interest_score > 90 && (
          <div className="absolute top-4 left-4 bg-red-500 text-white px-3 py-2 rounded-full text-sm font-bold">
            🔥 Highly Popular ({motorcycle.user_interest_score}/100)
          </div>
        )}
      </div>
      <div className="p-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-3xl font-bold text-gray-800">{motorcycle.manufacturer} {motorcycle.model}</h2>
            <p className="text-lg text-gray-600">{motorcycle.year} • {motorcycle.category}</p>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold text-green-600">${motorcycle.price_usd.toLocaleString()}</div>
            <div className="text-sm text-gray-500">{motorcycle.availability}</div>
          </div>
        </div>
        
        <p className="text-gray-700 mb-6 leading-relaxed">{motorcycle.description}</p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div className="bg-gray-50 p-6 rounded-lg">
            <h3 className="text-lg font-semibold mb-4 text-gray-800">Engine Specifications</h3>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-600">Engine Type:</span>
                <span className="font-medium">{motorcycle.engine_type}</span>
              </div>
              {motorcycle.displacement > 0 && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Displacement:</span>
                  <span className="font-medium">{motorcycle.displacement}cc</span>
                </div>
              )}
              <div className="flex justify-between">
                <span className="text-gray-600">Horsepower:</span>
                <span className="font-medium">{motorcycle.horsepower}hp</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Torque:</span>
                <span className="font-medium">{motorcycle.torque}Nm</span>
              </div>
            </div>
          </div>
          
          <div className="bg-gray-50 p-6 rounded-lg">
            <h3 className="text-lg font-semibold mb-4 text-gray-800">Performance & Specs</h3>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-600">Top Speed:</span>
                <span className="font-medium">{motorcycle.top_speed} km/h</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Weight:</span>
                <span className="font-medium">{motorcycle.weight}kg</span>
              </div>
              {motorcycle.fuel_capacity > 0 && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Fuel Capacity:</span>
                  <span className="font-medium">{motorcycle.fuel_capacity}L</span>
                </div>
              )}
              <div className="flex justify-between">
                <span className="text-gray-600">User Interest:</span>
                <span className="font-medium">{motorcycle.user_interest_score}/100</span>
              </div>
            </div>
          </div>
        </div>
        
        <div className="bg-blue-50 p-6 rounded-lg">
          <h3 className="text-lg font-semibold mb-4 text-gray-800">Key Features</h3>
          <div className="flex flex-wrap gap-2">
            {motorcycle.features.map((feature, index) => (
              <span key={index} className="bg-blue-600 text-white px-3 py-1 rounded-full text-sm">
                {feature}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  </div>
);

const FilterSidebar = ({ filters, onFilterChange, filterOptions, isOpen, onToggle }) => (
  <div className={`bg-white p-6 rounded-xl shadow-lg ${isOpen ? 'block' : 'hidden'} lg:block`}>
    <div className="flex items-center justify-between mb-6">
      <h3 className="text-lg font-semibold text-gray-800">Filters</h3>
      <button onClick={onToggle} className="lg:hidden">
        <span className="text-gray-500">×</span>
      </button>
    </div>
    
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Search</label>
        <input
          type="text"
          placeholder="Search motorcycles..."
          value={filters.search || ''}
          onChange={(e) => onFilterChange({ ...filters, search: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Manufacturer</label>
        <select
          value={filters.manufacturer || ''}
          onChange={(e) => onFilterChange({ ...filters, manufacturer: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="">All Manufacturers</option>
          {filterOptions.manufacturers?.map(manufacturer => (
            <option key={manufacturer} value={manufacturer}>{manufacturer}</option>
          ))}
        </select>
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
        <select
          value={filters.category || ''}
          onChange={(e) => onFilterChange({ ...filters, category: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="">All Categories</option>
          {filterOptions.categories?.map(category => (
            <option key={category} value={category}>{category}</option>
          ))}
        </select>
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Year Range</label>
        <div className="flex space-x-2">
          <input
            type="number"
            placeholder="From"
            value={filters.year_min || ''}
            onChange={(e) => onFilterChange({ ...filters, year_min: e.target.value ? parseInt(e.target.value) : null })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <input
            type="number"
            placeholder="To"
            value={filters.year_max || ''}
            onChange={(e) => onFilterChange({ ...filters, year_max: e.target.value ? parseInt(e.target.value) : null })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Price Range (USD)</label>
        <div className="flex space-x-2">
          <input
            type="number"
            placeholder="Min"
            value={filters.price_min || ''}
            onChange={(e) => onFilterChange({ ...filters, price_min: e.target.value ? parseInt(e.target.value) : null })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <input
            type="number"
            placeholder="Max"
            value={filters.price_max || ''}
            onChange={(e) => onFilterChange({ ...filters, price_max: e.target.value ? parseInt(e.target.value) : null })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>
      
      <button
        onClick={() => onFilterChange({})}
        className="w-full bg-gray-200 text-gray-800 py-2 px-4 rounded-lg hover:bg-gray-300 transition-colors"
      >
        Clear All Filters
      </button>
    </div>
  </div>
);

function App() {
  const [currentView, setCurrentView] = useState('home'); // 'home' or 'browse'
  const [motorcycles, setMotorcycles] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedMotorcycle, setSelectedMotorcycle] = useState(null);
  const [filters, setFilters] = useState({});
  const [filterOptions, setFilterOptions] = useState({});
  const [sortBy, setSortBy] = useState('user_interest_score');
  const [sortOrder, setSortOrder] = useState('desc');
  const [showFilters, setShowFilters] = useState(false);

  const fetchMotorcycles = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== null && value !== '' && value !== undefined) {
          params.append(key, value);
        }
      });
      
      params.append('sort_by', sortBy);
      params.append('sort_order', sortOrder);
      
      const response = await axios.get(`${API}/motorcycles?${params.toString()}`);
      setMotorcycles(response.data);
    } catch (error) {
      console.error('Error fetching motorcycles:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await axios.get(`${API}/motorcycles/categories/summary`);
      setCategories(response.data);
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const fetchFilterOptions = async () => {
    try {
      const response = await axios.get(`${API}/motorcycles/filters/options`);
      setFilterOptions(response.data);
    } catch (error) {
      console.error('Error fetching filter options:', error);
    }
  };

  const seedDatabase = async () => {
    try {
      await axios.post(`${API}/motorcycles/seed`);
      fetchCategories();
      fetchMotorcycles();
    } catch (error) {
      console.error('Error seeding database:', error);
    }
  };

  useEffect(() => {
    fetchFilterOptions();
    seedDatabase(); // Seed on first load
  }, []);

  useEffect(() => {
    if (currentView === 'browse') {
      fetchMotorcycles();
    }
  }, [filters, sortBy, sortOrder, currentView]);

  const totalMotorcycles = categories.reduce((sum, cat) => sum + cat.count, 0);
  const totalManufacturers = filterOptions.manufacturers?.length || 0;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <button 
                onClick={() => setCurrentView('home')}
                className="text-2xl font-bold text-gray-900 hover:text-blue-600 transition-colors"
              >
                Byke-Dream
              </button>
              <span className="ml-2 text-sm text-gray-500">Motorcycle Database</span>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setCurrentView('home')}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  currentView === 'home' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:text-blue-600'
                }`}
              >
                Home
              </button>
              <button
                onClick={() => setCurrentView('browse')}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  currentView === 'browse' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:text-blue-600'
                }`}
              >
                Browse All
              </button>
              {currentView === 'browse' && (
                <>
                  <select
                    value={`${sortBy}-${sortOrder}`}
                    onChange={(e) => {
                      const [newSortBy, newSortOrder] = e.target.value.split('-');
                      setSortBy(newSortBy);
                      setSortOrder(newSortOrder);
                    }}
                    className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="user_interest_score-desc">Most Popular</option>
                    <option value="year-desc">Newest First</option>
                    <option value="year-asc">Oldest First</option>
                    <option value="price_usd-asc">Price: Low to High</option>
                    <option value="price_usd-desc">Price: High to Low</option>
                    <option value="horsepower-desc">Most Powerful</option>
                  </select>
                  <button
                    onClick={() => setShowFilters(!showFilters)}
                    className="lg:hidden bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Filters
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      </header>

      {currentView === 'home' ? (
        // Home Page
        <>
          {/* Hero Section */}
          <div className="bg-gradient-to-r from-blue-900 via-blue-800 to-indigo-900 text-white">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
              <div className="text-center">
                <h2 className="text-5xl font-bold mb-6">Discover Your Dream Motorcycle</h2>
                <p className="text-xl mb-8 text-blue-100">
                  The world's most comprehensive motorcycle database spanning from 1900 to present day
                </p>
                <div className="flex justify-center space-x-12 text-lg mb-8">
                  <div className="text-center">
                    <div className="text-4xl font-bold text-blue-300">{totalMotorcycles}+</div>
                    <div className="text-blue-100">Motorcycles</div>
                  </div>
                  <div className="text-center">
                    <div className="text-4xl font-bold text-blue-300">125+</div>
                    <div className="text-blue-100">Years of History</div>
                  </div>
                  <div className="text-center">
                    <div className="text-4xl font-bold text-blue-300">{totalManufacturers}+</div>
                    <div className="text-blue-100">Manufacturers</div>
                  </div>
                </div>
                <button
                  onClick={() => setCurrentView('browse')}
                  className="bg-white text-blue-900 px-8 py-4 rounded-lg text-lg font-semibold hover:bg-blue-50 transition-colors"
                >
                  Explore All Motorcycles
                </button>
              </div>
            </div>
          </div>

          {/* Categories Section */}
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
            <div className="text-center mb-12">
              <h2 className="text-4xl font-bold text-gray-800 mb-4">Motorcycles by Category</h2>
              <p className="text-xl text-gray-600">
                Curated collections based on user interest and popularity
              </p>
            </div>

            {loading ? (
              <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
              </div>
            ) : (
              <div className="space-y-16">
                {categories.map((category) => (
                  <CategorySection
                    key={category.category}
                    category={category}
                    onMotorcycleClick={setSelectedMotorcycle}
                  />
                ))}
              </div>
            )}
          </div>
        </>
      ) : (
        // Browse Page
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex flex-col lg:flex-row gap-8">
            {/* Sidebar */}
            <div className="lg:w-80 flex-shrink-0">
              <FilterSidebar
                filters={filters}
                onFilterChange={setFilters}
                filterOptions={filterOptions}
                isOpen={showFilters}
                onToggle={() => setShowFilters(!showFilters)}
              />
            </div>

            {/* Motorcycle Grid */}
            <div className="flex-1">
              <div className="mb-6">
                <h1 className="text-3xl font-bold text-gray-800">
                  All Motorcycles ({motorcycles.length})
                </h1>
                <p className="text-gray-600">Complete motorcycle database from 1900 to present</p>
              </div>

              {loading ? (
                <div className="flex justify-center items-center h-64">
                  <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
                </div>
              ) : motorcycles.length === 0 ? (
                <div className="text-center py-12">
                  <div className="text-gray-500 text-lg">No motorcycles found matching your criteria</div>
                  <button
                    onClick={() => setFilters({})}
                    className="mt-4 bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Clear Filters
                  </button>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                  {motorcycles.map((motorcycle) => (
                    <MotorcycleCard
                      key={motorcycle.id}
                      motorcycle={motorcycle}
                      onClick={setSelectedMotorcycle}
                    />
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Modal */}
      {selectedMotorcycle && (
        <MotorcycleDetail
          motorcycle={selectedMotorcycle}
          onClose={() => setSelectedMotorcycle(null)}
        />
      )}
    </div>
  );
}

export default App;