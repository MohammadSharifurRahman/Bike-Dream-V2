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
              <div className="flex justify-between">
                <span className="text-gray-600">Displacement:</span>
                <span className="font-medium">{motorcycle.displacement}cc</span>
              </div>
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
              <div className="flex justify-between">
                <span className="text-gray-600">Fuel Capacity:</span>
                <span className="font-medium">{motorcycle.fuel_capacity}L</span>
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
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Engine Size (cc)</label>
        <div className="flex space-x-2">
          <input
            type="number"
            placeholder="Min"
            value={filters.displacement_min || ''}
            onChange={(e) => onFilterChange({ ...filters, displacement_min: e.target.value ? parseInt(e.target.value) : null })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <input
            type="number"
            placeholder="Max"
            value={filters.displacement_max || ''}
            onChange={(e) => onFilterChange({ ...filters, displacement_max: e.target.value ? parseInt(e.target.value) : null })}
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
  const [motorcycles, setMotorcycles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedMotorcycle, setSelectedMotorcycle] = useState(null);
  const [filters, setFilters] = useState({});
  const [filterOptions, setFilterOptions] = useState({});
  const [sortBy, setSortBy] = useState('year');
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
    fetchMotorcycles();
  }, [filters, sortBy, sortOrder]);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">Byke-Dream</h1>
              <span className="ml-2 text-sm text-gray-500">Motorcycle Database</span>
            </div>
            <div className="flex items-center space-x-4">
              <select
                value={`${sortBy}-${sortOrder}`}
                onChange={(e) => {
                  const [newSortBy, newSortOrder] = e.target.value.split('-');
                  setSortBy(newSortBy);
                  setSortOrder(newSortOrder);
                }}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="year-desc">Newest First</option>
                <option value="year-asc">Oldest First</option>
                <option value="price_usd-asc">Price: Low to High</option>
                <option value="price_usd-desc">Price: High to Low</option>
                <option value="horsepower-desc">Most Powerful</option>
                <option value="model-asc">Name A-Z</option>
              </select>
              <button
                onClick={() => setShowFilters(!showFilters)}
                className="lg:hidden bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
              >
                Filters
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-900 via-blue-800 to-indigo-900 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="text-center">
            <h2 className="text-5xl font-bold mb-6">Discover Your Dream Motorcycle</h2>
            <p className="text-xl mb-8 text-blue-100">Explore the world's most comprehensive motorcycle database from 1900 to present</p>
            <div className="flex justify-center space-x-8 text-lg">
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-300">{motorcycles.length}+</div>
                <div className="text-blue-100">Motorcycles</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-300">125+</div>
                <div className="text-blue-100">Years of History</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-300">{filterOptions.manufacturers?.length || 0}+</div>
                <div className="text-blue-100">Manufacturers</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
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