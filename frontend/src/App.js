import React, { useState, useEffect, createContext, useContext } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Authentication Context
const AuthContext = createContext();

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for existing authentication
    const token = localStorage.getItem('auth_token');
    const sessionId = localStorage.getItem('session_id');
    
    // Handle Google OAuth callback
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    
    if (code && window.location.pathname === '/auth/google/callback') {
      handleGoogleCallback(code);
      return;
    }
    
    if (token) {
      // Try JWT token first
      validateToken();
    } else if (sessionId) {
      // Fall back to session ID
      validateSession();
    } else {
      setLoading(false);
    }
  }, []);

  const handleGoogleCallback = async (code) => {
    try {
      setLoading(true);
      const response = await axios.post(`${API}/auth/google/callback`, { code });
      
      localStorage.setItem('auth_token', response.data.token);
      setUser(response.data.user);
      
      // Redirect back to original location
      const redirectPath = localStorage.getItem('auth_redirect') || '/';
      localStorage.removeItem('auth_redirect');
      window.history.replaceState({}, '', redirectPath);
      
    } catch (error) {
      console.error('Google OAuth callback error:', error);
      // Redirect to login page with error
      window.history.replaceState({}, '', '/?auth_error=google_failed');
    } finally {
      setLoading(false);
    }
  };

  const validateToken = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await axios.get(`${API}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUser(response.data);
    } catch (error) {
      localStorage.removeItem('auth_token');
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const validateSession = async () => {
    try {
      const sessionId = localStorage.getItem('session_id');
      const response = await axios.get(`${API}/auth/me`, {
        headers: { 'X-Session-ID': sessionId }
      });
      setUser(response.data);
    } catch (error) {
      localStorage.removeItem('session_id');
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const register = async (email, password, name) => {
    try {
      const response = await axios.post(`${API}/auth/register`, {
        email,
        password,
        name
      });
      
      localStorage.setItem('auth_token', response.data.token);
      setUser(response.data.user);
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Registration failed' 
      };
    }
  };

  const login = async (email, password) => {
    try {
      const response = await axios.post(`${API}/auth/login`, {
        email,
        password
      });
      
      localStorage.setItem('auth_token', response.data.token);
      setUser(response.data.user);
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Login failed' 
      };
    }
  };

  const loginWithGoogle = async () => {
    try {
      // Use Google OAuth 2.0 flow
      const clientId = process.env.REACT_APP_GOOGLE_CLIENT_ID || "your-google-client-id";
      const redirectUri = encodeURIComponent(window.location.origin + '/auth/google/callback');
      const scope = encodeURIComponent('https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email');
      
      const googleAuthUrl = `https://accounts.google.com/o/oauth2/v2/auth?` +
        `client_id=${clientId}&` +
        `redirect_uri=${redirectUri}&` +
        `response_type=code&` +
        `scope=${scope}&` +
        `access_type=offline`;
      
      // Store current location to redirect back after auth
      localStorage.setItem('auth_redirect', window.location.pathname);
      
      // Redirect to Google OAuth
      window.location.href = googleAuthUrl;
      
    } catch (error) {
      console.error('Google OAuth error:', error);
      return { 
        success: false, 
        error: 'Google login failed. Please try again.' 
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('session_id');
    setUser(null);
  };

  const legacyLogin = () => {
    // Legacy Emergent login (keeping for backward compatibility)
    window.location.href = 'https://demobackend.emergentagent.com/auth/v1/env/oauth/login?redirect_url=' + 
      encodeURIComponent(window.location.origin + '/profile');
  };

  return (
    <AuthContext.Provider value={{ 
      user, 
      loading, 
      register, 
      login, 
      loginWithGoogle, 
      logout, 
      legacyLogin 
    }}>
      {children}
    </AuthContext.Provider>
  );
};

const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Star Rating Component
const StarRating = ({ rating, onRatingChange, readOnly = false }) => {
  const [hoverRating, setHoverRating] = useState(0);

  return (
    <div className="flex space-x-1">
      {[1, 2, 3, 4, 5].map((star) => (
        <button
          key={star}
          className={`text-2xl transition-colors ${
            star <= (hoverRating || rating)
              ? 'text-yellow-400'
              : 'text-gray-300'
          } ${readOnly ? 'cursor-default' : 'cursor-pointer hover:text-yellow-400'}`}
          onClick={() => !readOnly && onRatingChange && onRatingChange(star)}
          onMouseEnter={() => !readOnly && setHoverRating(star)}
          onMouseLeave={() => !readOnly && setHoverRating(0)}
          disabled={readOnly}
        >
          ★
        </button>
      ))}
    </div>
  );
};

// Vendor Pricing Component
const VendorPricing = ({ motorcycle }) => {
  const [vendorPrices, setVendorPrices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedRegion, setSelectedRegion] = useState('US');
  const [regions, setRegions] = useState([]);

  useEffect(() => {
    fetchRegions();
  }, []);

  useEffect(() => {
    if (motorcycle) {
      fetchVendorPricing();
    }
  }, [motorcycle, selectedRegion]);

  const fetchRegions = async () => {
    try {
      const response = await axios.get(`${API}/pricing/regions`);
      setRegions(response.data.regions || []);
    } catch (error) {
      console.error('Error fetching regions:', error);
    }
  };

  const fetchVendorPricing = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/motorcycles/${motorcycle.id}/pricing?region=${selectedRegion}`);
      setVendorPrices(response.data.vendor_prices || []);
    } catch (error) {
      console.error('Error fetching vendor pricing:', error);
      setVendorPrices([]);
    } finally {
      setLoading(false);
    }
  };

  const formatPrice = (price, currency) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(price);
  };

  const getRegionName = (regionCode) => {
    const regionNames = {
      'US': 'United States',
      // South Asian countries
      'BD': 'Bangladesh',
      'IN': 'India',
      'NP': 'Nepal',
      'BT': 'Bhutan',
      'PK': 'Pakistan',
      'LK': 'Sri Lanka',
      // Southeast Asian countries
      'TH': 'Thailand',
      'MY': 'Malaysia',
      'ID': 'Indonesia',
      'PH': 'Philippines',
      'VN': 'Vietnam',
      'SG': 'Singapore',
      // East Asian countries
      'JP': 'Japan',
      'KR': 'South Korea',
      'TW': 'Taiwan',
      'CN': 'China',
      'HK': 'Hong Kong',
      // Middle Eastern countries
      'AE': 'UAE',
      'SA': 'Saudi Arabia',
      'QA': 'Qatar',
      'KW': 'Kuwait',
      'BH': 'Bahrain',
      'OM': 'Oman',
      'JO': 'Jordan',
      'TR': 'Turkey',
      'IL': 'Israel',
      // European countries
      'GB': 'United Kingdom',
      'DE': 'Germany',
      'FR': 'France',
      'IT': 'Italy',
      'ES': 'Spain',
      'NL': 'Netherlands',
      'BE': 'Belgium',
      'AT': 'Austria',
      'PT': 'Portugal',
      'IE': 'Ireland',
      'FI': 'Finland',
      'CH': 'Switzerland',
      'NO': 'Norway',
      'SE': 'Sweden',
      'DK': 'Denmark',
      'PL': 'Poland',
      'CZ': 'Czech Republic',
      'HU': 'Hungary',
      'RO': 'Romania',
      // Americas
      'CA': 'Canada',
      'BR': 'Brazil',
      'MX': 'Mexico',
      'AR': 'Argentina',
      'CL': 'Chile',
      'CO': 'Colombia',
      'PE': 'Peru',
      // Oceania
      'AU': 'Australia',
      'NZ': 'New Zealand',
      // African countries
      'ZA': 'South Africa',
      'EG': 'Egypt',
      'NG': 'Nigeria',
      'KE': 'Kenya',
      // Other regions
      'RU': 'Russia',
      'UA': 'Ukraine'
    };
    return regionNames[regionCode] || regionCode;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Select Region
        </label>
        <select
          value={selectedRegion}
          onChange={(e) => setSelectedRegion(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="US">🇺🇸 United States (USD)</option>
          
          <optgroup label="🌏 South Asia">
            <option value="BD">🇧🇩 Bangladesh (BDT)</option>
            <option value="IN">🇮🇳 India (INR)</option>
            <option value="NP">🇳🇵 Nepal (NPR)</option>
            <option value="BT">🇧🇹 Bhutan (BTN)</option>
            <option value="PK">🇵🇰 Pakistan (PKR)</option>
            <option value="LK">🇱🇰 Sri Lanka (LKR)</option>
          </optgroup>
          
          <optgroup label="🌏 Southeast Asia">
            <option value="TH">🇹🇭 Thailand (THB)</option>
            <option value="MY">🇲🇾 Malaysia (MYR)</option>
            <option value="ID">🇮🇩 Indonesia (IDR)</option>
            <option value="PH">🇵🇭 Philippines (PHP)</option>
            <option value="VN">🇻🇳 Vietnam (VND)</option>
            <option value="SG">🇸🇬 Singapore (SGD)</option>
          </optgroup>
          
          <optgroup label="🌏 East Asia">
            <option value="JP">🇯🇵 Japan (JPY)</option>
            <option value="KR">🇰🇷 South Korea (KRW)</option>
            <option value="TW">🇹🇼 Taiwan (TWD)</option>
            <option value="CN">🇨🇳 China (CNY)</option>
            <option value="HK">🇭🇰 Hong Kong (HKD)</option>
          </optgroup>
          
          <optgroup label="🌍 Middle East">
            <option value="AE">🇦🇪 UAE (AED)</option>
            <option value="SA">🇸🇦 Saudi Arabia (SAR)</option>
            <option value="QA">🇶🇦 Qatar (QAR)</option>
            <option value="KW">🇰🇼 Kuwait (KWD)</option>
            <option value="BH">🇧🇭 Bahrain (BHD)</option>
            <option value="OM">🇴🇲 Oman (OMR)</option>
            <option value="JO">🇯🇴 Jordan (JOD)</option>
            <option value="TR">🇹🇷 Turkey (TRY)</option>
            <option value="IL">🇮🇱 Israel (ILS)</option>
          </optgroup>
          
          <optgroup label="🇪🇺 Europe">
            <option value="GB">🇬🇧 United Kingdom (GBP)</option>
            <option value="DE">🇩🇪 Germany (EUR)</option>
            <option value="FR">🇫🇷 France (EUR)</option>
            <option value="IT">🇮🇹 Italy (EUR)</option>
            <option value="ES">🇪🇸 Spain (EUR)</option>
            <option value="NL">🇳🇱 Netherlands (EUR)</option>
            <option value="BE">🇧🇪 Belgium (EUR)</option>
            <option value="AT">🇦🇹 Austria (EUR)</option>
            <option value="PT">🇵🇹 Portugal (EUR)</option>
            <option value="IE">🇮🇪 Ireland (EUR)</option>
            <option value="FI">🇫🇮 Finland (EUR)</option>
            <option value="CH">🇨🇭 Switzerland (CHF)</option>
            <option value="NO">🇳🇴 Norway (NOK)</option>
            <option value="SE">🇸🇪 Sweden (SEK)</option>
            <option value="DK">🇩🇰 Denmark (DKK)</option>
            <option value="PL">🇵🇱 Poland (PLN)</option>
            <option value="CZ">🇨🇿 Czech Republic (CZK)</option>
            <option value="HU">🇭🇺 Hungary (HUF)</option>
            <option value="RO">🇷🇴 Romania (RON)</option>
          </optgroup>
          
          <optgroup label="🌎 Americas">
            <option value="CA">🇨🇦 Canada (CAD)</option>
            <option value="BR">🇧🇷 Brazil (BRL)</option>
            <option value="MX">🇲🇽 Mexico (MXN)</option>
            <option value="AR">🇦🇷 Argentina (ARS)</option>
            <option value="CL">🇨🇱 Chile (CLP)</option>
            <option value="CO">🇨🇴 Colombia (COP)</option>
            <option value="PE">🇵🇪 Peru (PEN)</option>
          </optgroup>
          
          <optgroup label="🌏 Oceania">
            <option value="AU">🇦🇺 Australia (AUD)</option>
            <option value="NZ">🇳🇿 New Zealand (NZD)</option>
          </optgroup>
          
          <optgroup label="🌍 Africa">
            <option value="ZA">🇿🇦 South Africa (ZAR)</option>
            <option value="EG">🇪🇬 Egypt (EGP)</option>
            <option value="NG">🇳🇬 Nigeria (NGN)</option>
            <option value="KE">🇰🇪 Kenya (KES)</option>
          </optgroup>
          
          <optgroup label="🌍 Other Regions">
            <option value="RU">🇷🇺 Russia (RUB)</option>
            <option value="UA">🇺🇦 Ukraine (UAH)</option>
          </optgroup>
        </select>
      </div>

      {vendorPrices.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          No vendor pricing available for this region
        </div>
      ) : vendorPrices[0]?.discontinued ? (
        <div className="text-center py-8">
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
            <div className="text-yellow-800 text-lg font-semibold mb-2">
              Motorcycle Discontinued
            </div>
            <p className="text-yellow-700">
              This motorcycle model is no longer in production. Prices are not available from authorized dealers.
              You may find used models through private sellers or specialty dealers.
            </p>
          </div>
        </div>
      ) : vendorPrices[0]?.not_available_in_region ? (
        <div className="text-center py-8">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
            <div className="text-blue-800 text-lg font-semibold mb-2">
              Not Available in This Region
            </div>
            <p className="text-blue-700 mb-3">
              {vendorPrices[0].availability}
            </p>
            {vendorPrices[0].reason && (
              <p className="text-blue-600 text-sm">
                <strong>Reason:</strong> {vendorPrices[0].reason}
              </p>
            )}
            <div className="mt-4 p-3 bg-blue-100 rounded">
              <p className="text-blue-800 text-sm">
                💡 <strong>Tip:</strong> Try selecting a different region or contact local importers for availability.
              </p>
            </div>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {vendorPrices.map((vendor, index) => (
            <div key={index} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <div>
                  <h4 className="font-semibold text-lg text-gray-800">{vendor.vendor_name}</h4>
                  <div className="flex items-center space-x-2 text-sm text-gray-500">
                    <span>⭐ {vendor.rating}</span>
                    <span>({vendor.reviews_count} reviews)</span>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-green-600">
                    {formatPrice(vendor.price, vendor.currency)}
                  </div>
                  {vendor.currency !== 'USD' && (
                    <div className="text-sm text-gray-500">
                      ≈ {formatPrice(vendor.price_usd, 'USD')}
                    </div>
                  )}
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4 text-sm mb-4">
                <div>
                  <span className="text-gray-600">Availability:</span>
                  <span className={`ml-2 px-2 py-1 rounded-full text-xs ${
                    vendor.availability === 'In Stock' ? 'bg-green-100 text-green-800' :
                    vendor.availability === 'Limited Stock' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-blue-100 text-blue-800'
                  }`}>
                    {vendor.availability}
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">Shipping:</span>
                  <span className="ml-2 font-medium">{vendor.shipping}</span>
                </div>
                <div>
                  <span className="text-gray-600">Delivery:</span>
                  <span className="ml-2 font-medium">{vendor.estimated_delivery}</span>
                </div>
                {vendor.phone && (
                  <div>
                    <span className="text-gray-600">Phone:</span>
                    <span className="ml-2 font-medium">{vendor.phone}</span>
                  </div>
                )}
              </div>

              {vendor.special_offer && (
                <div className="bg-blue-50 border border-blue-200 rounded p-3 mb-4">
                  <div className="text-blue-800 font-medium">🎁 Special Offer</div>
                  <div className="text-blue-700">{vendor.special_offer}</div>
                </div>
              )}

              <div className="flex space-x-3">
                {vendor.website_url && (
                  <a
                    href={vendor.website_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex-1 bg-blue-600 text-white text-center py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Visit Store
                  </a>
                )}
                <button className="bg-gray-200 text-gray-800 px-4 py-2 rounded-lg hover:bg-gray-300 transition-colors">
                  Compare
                </button>
              </div>
            </div>
          ))}
          
          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <div className="text-sm text-gray-600">
              <p className="mb-2">
                <strong>Note:</strong> Prices shown are from verified dealers and may vary based on location, taxes, and current promotions.
              </p>
              <p>
                All vendor links have been verified and lead to legitimate dealership websites.
                Prices are updated regularly to reflect current market conditions.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Rating and Review Component
const RatingSection = ({ motorcycle, onRatingSubmit }) => {
  const { user } = useAuth();
  const [ratings, setRatings] = useState([]);
  const [userRating, setUserRating] = useState(0);
  const [userReview, setUserReview] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [hasUserRated, setHasUserRated] = useState(false);

  useEffect(() => {
    fetchRatings();
  }, [motorcycle.id]);

  const fetchRatings = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/motorcycles/${motorcycle.id}/ratings`);
      setRatings(response.data || []);
      
      // Check if current user has already rated this motorcycle
      if (user) {
        const existingRating = response.data.find(rating => rating.user_id === user.id);
        if (existingRating) {
          setHasUserRated(true);
          setUserRating(existingRating.rating);
          setUserReview(existingRating.review_text || '');
        }
      }
    } catch (error) {
      console.error('Error fetching ratings:', error);
      setRatings([]);
    } finally {
      setLoading(false);
    }
  };

  const handleRatingSubmit = async (e) => {
    e.preventDefault();
    
    if (!user) {
      alert('Please login to rate this motorcycle');
      return;
    }

    if (userRating === 0) {
      alert('Please select a star rating');
      return;
    }

    try {
      setSubmitting(true);
      const token = localStorage.getItem('auth_token');
      const sessionId = localStorage.getItem('session_id');
      
      const headers = {};
      if (token) {
        headers.Authorization = `Bearer ${token}`;
      } else if (sessionId) {
        headers['X-Session-ID'] = sessionId;
      }

      await axios.post(`${API}/motorcycles/${motorcycle.id}/rate`, {
        motorcycle_id: motorcycle.id,
        rating: userRating,
        review_text: userReview.trim() || null
      }, { headers });

      // Refresh ratings after successful submission
      await fetchRatings();
      
      if (onRatingSubmit) {
        onRatingSubmit();
      }

      alert(hasUserRated ? 'Rating updated successfully!' : 'Rating submitted successfully!');
    } catch (error) {
      console.error('Error submitting rating:', error);
      alert('Error submitting rating. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const calculateAverageRating = () => {
    if (ratings.length === 0) return 0;
    const sum = ratings.reduce((acc, rating) => acc + rating.rating, 0);
    return (sum / ratings.length).toFixed(1);
  };

  const getRatingDistribution = () => {
    const distribution = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 };
    ratings.forEach(rating => {
      distribution[rating.rating]++;
    });
    return distribution;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const averageRating = calculateAverageRating();
  const distribution = getRatingDistribution();

  return (
    <div className="space-y-6">
      {/* Rating Overview */}
      <div className="bg-gray-50 p-6 rounded-lg">
        <div className="flex items-center space-x-4 mb-4">
          <div className="text-center">
            <div className="text-4xl font-bold text-gray-800">{averageRating}</div>
            <StarRating rating={Math.round(parseFloat(averageRating))} readOnly />
            <div className="text-sm text-gray-500 mt-1">{ratings.length} reviews</div>
          </div>
          <div className="flex-1">
            {[5, 4, 3, 2, 1].map(star => (
              <div key={star} className="flex items-center space-x-2 mb-1">
                <span className="text-sm w-8">{star}★</span>
                <div className="flex-1 bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-yellow-400 h-2 rounded-full" 
                    style={{ width: `${ratings.length > 0 ? (distribution[star] / ratings.length) * 100 : 0}%` }}
                  ></div>
                </div>
                <span className="text-sm text-gray-500 w-8">{distribution[star]}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* User Rating Form */}
      {user ? (
        <div className="bg-white border rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">
            {hasUserRated ? 'Update Your Rating' : 'Rate This Motorcycle'}
          </h3>
          <form onSubmit={handleRatingSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Your Rating *
              </label>
              <StarRating 
                rating={userRating} 
                onRatingChange={setUserRating}
                readOnly={false}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Review (Optional)
              </label>
              <textarea
                value={userReview}
                onChange={(e) => setUserReview(e.target.value)}
                placeholder="Share your experience with this motorcycle..."
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                maxLength={500}
              />
              <div className="text-right text-sm text-gray-500 mt-1">
                {userReview.length}/500 characters
              </div>
            </div>
            <button
              type="submit"
              disabled={submitting || userRating === 0}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {submitting ? 'Submitting...' : (hasUserRated ? 'Update Rating' : 'Submit Rating')}
            </button>
          </form>
        </div>
      ) : (
        <div className="bg-gray-50 border rounded-lg p-6 text-center">
          <p className="text-gray-600 mb-4">Please login to rate this motorcycle</p>
          <AuthButton />
        </div>
      )}

      {/* Reviews List */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold">User Reviews ({ratings.length})</h3>
        {ratings.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            No reviews yet. Be the first to rate this motorcycle!
          </div>
        ) : (
          ratings.map((rating) => (
            <div key={rating.id} className="bg-white border rounded-lg p-4">
              <div className="flex items-start space-x-3">
                <img 
                  src={rating.user_picture || `https://ui-avatars.com/api/?name=${encodeURIComponent(rating.user_name)}&background=0D8ABC&color=fff`} 
                  alt={rating.user_name}
                  className="w-10 h-10 rounded-full"
                />
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-1">
                    <span className="font-medium text-gray-800">{rating.user_name}</span>
                    <StarRating rating={rating.rating} readOnly />
                    <span className="text-sm text-gray-500">
                      {new Date(rating.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  {rating.review_text && (
                    <p className="text-gray-700 mt-2">{rating.review_text}</p>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

// Comments Section Component
const DiscussionSection = ({ motorcycle }) => {
  const { user } = useAuth();
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');
  const [replyTo, setReplyTo] = useState(null);
  const [replyText, setReplyText] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchComments();
  }, [motorcycle.id]);

  const fetchComments = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/motorcycles/${motorcycle.id}/comments?include_replies=true`);
      setComments(response.data || []);
    } catch (error) {
      console.error('Error fetching comments:', error);
      setComments([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitComment = async (e) => {
    e.preventDefault();
    if (!user) {
      alert('Please login to post comments');
      return;
    }

    if (!newComment.trim()) {
      alert('Please enter a comment');
      return;
    }

    try {
      setSubmitting(true);
      const token = localStorage.getItem('auth_token');
      const sessionId = localStorage.getItem('session_id');
      
      const headers = {};
      if (token) {
        headers.Authorization = `Bearer ${token}`;
      } else if (sessionId) {
        headers['X-Session-ID'] = sessionId;
      }

      await axios.post(`${API}/motorcycles/${motorcycle.id}/comment`, {
        motorcycle_id: motorcycle.id,
        content: newComment.trim()
      }, { headers });

      setNewComment('');
      await fetchComments(); // Refresh comments
    } catch (error) {
      console.error('Error posting comment:', error);
      alert('Error posting comment. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleSubmitReply = async (parentCommentId) => {
    if (!user) {
      alert('Please login to reply');
      return;
    }

    if (!replyText.trim()) {
      alert('Please enter a reply');
      return;
    }

    try {
      setSubmitting(true);
      const token = localStorage.getItem('auth_token');
      const sessionId = localStorage.getItem('session_id');
      
      const headers = {};
      if (token) {
        headers.Authorization = `Bearer ${token}`;
      } else if (sessionId) {
        headers['X-Session-ID'] = sessionId;
      }

      await axios.post(`${API}/motorcycles/${motorcycle.id}/comment`, {
        motorcycle_id: motorcycle.id,
        content: replyText.trim(),
        parent_comment_id: parentCommentId
      }, { headers });

      setReplyText('');
      setReplyTo(null);
      await fetchComments(); // Refresh comments
    } catch (error) {
      console.error('Error posting reply:', error);
      alert('Error posting reply. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleLikeComment = async (commentId) => {
    if (!user) {
      alert('Please login to like comments');
      return;
    }

    try {
      const token = localStorage.getItem('auth_token');
      const sessionId = localStorage.getItem('session_id');
      
      const headers = {};
      if (token) {
        headers.Authorization = `Bearer ${token}`;
      } else if (sessionId) {
        headers['X-Session-ID'] = sessionId;
      }

      await axios.post(`${API}/comments/${commentId}/like`, {}, { headers });
      await fetchComments(); // Refresh to update like counts
    } catch (error) {
      console.error('Error liking comment:', error);
    }
  };

  const handleDeleteComment = async (commentId) => {
    if (!user) return;

    if (!confirm('Are you sure you want to delete this comment?')) return;

    try {
      const token = localStorage.getItem('auth_token');
      const sessionId = localStorage.getItem('session_id');
      
      const headers = {};
      if (token) {
        headers.Authorization = `Bearer ${token}`;
      } else if (sessionId) {
        headers['X-Session-ID'] = sessionId;
      }

      await axios.delete(`${API}/comments/${commentId}`, { headers });
      await fetchComments(); // Refresh comments
    } catch (error) {
      console.error('Error deleting comment:', error);
      alert('Error deleting comment. Please try again.');
    }
  };

  const handleFlagComment = async (commentId) => {
    if (!user) {
      alert('Please login to flag comments');
      return;
    }

    if (!confirm('Are you sure you want to flag this comment as inappropriate?')) return;

    try {
      const token = localStorage.getItem('auth_token');
      const sessionId = localStorage.getItem('session_id');
      
      const headers = {};
      if (token) {
        headers.Authorization = `Bearer ${token}`;
      } else if (sessionId) {
        headers['X-Session-ID'] = sessionId;
      }

      await axios.post(`${API}/comments/${commentId}/flag`, {}, { headers });
      alert('Comment has been flagged for review. Thank you for helping keep our community safe.');
    } catch (error) {
      console.error('Error flagging comment:', error);
      alert('Error flagging comment. Please try again.');
    }
  };

  const formatTimeAgo = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInMinutes = Math.floor((now - date) / (1000 * 60));

    if (diffInMinutes < 1) return 'Just now';
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h ago`;
    if (diffInMinutes < 10080) return `${Math.floor(diffInMinutes / 1440)}d ago`;
    return date.toLocaleDateString();
  };

  const CommentItem = ({ comment, isReply = false }) => (
    <div className={`${isReply ? 'ml-8 border-l-2 border-gray-200 pl-4' : ''} mb-4`}>
      <div className="bg-white border rounded-lg p-4">
        <div className="flex items-start space-x-3">
          <img 
            src={comment.user_picture || `https://ui-avatars.com/api/?name=${encodeURIComponent(comment.user_name)}&background=0D8ABC&color=fff`}
            alt={comment.user_name}
            className="w-10 h-10 rounded-full"
          />
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-2">
              <span className="font-medium text-gray-800">{comment.user_name}</span>
              <span className="text-sm text-gray-500">{formatTimeAgo(comment.created_at)}</span>
              {comment.is_flagged && (
                <span className="text-xs bg-red-100 text-red-800 px-2 py-1 rounded">Flagged</span>
              )}
            </div>
            <p className="text-gray-700 mb-3">{comment.content}</p>
            
            <div className="flex items-center space-x-4 text-sm">
              <button
                onClick={() => handleLikeComment(comment.id)}
                className="flex items-center space-x-1 text-gray-500 hover:text-blue-600 transition-colors"
                disabled={!user}
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                </svg>
                <span>{comment.likes_count || 0}</span>
              </button>

              {!isReply && (
                <button
                  onClick={() => setReplyTo(replyTo === comment.id ? null : comment.id)}
                  className="text-gray-500 hover:text-blue-600 transition-colors"
                  disabled={!user}
                >
                  Reply ({comment.replies_count || 0})
                </button>
              )}

              {user && user.id === comment.user_id && (
                <button
                  onClick={() => handleDeleteComment(comment.id)}
                  className="text-gray-500 hover:text-red-600 transition-colors"
                >
                  Delete
                </button>
              )}

              {user && user.id !== comment.user_id && (
                <button
                  onClick={() => handleFlagComment(comment.id)}
                  className="text-gray-500 hover:text-red-600 transition-colors"
                >
                  Flag
                </button>
              )}
            </div>

            {/* Reply Form */}
            {replyTo === comment.id && (
              <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                <textarea
                  value={replyText}
                  onChange={(e) => setReplyText(e.target.value)}
                  placeholder="Write your reply..."
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  maxLength={1000}
                />
                <div className="flex items-center justify-between mt-2">
                  <span className="text-sm text-gray-500">{replyText.length}/1000 characters</span>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => {setReplyTo(null); setReplyText('');}}
                      className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-100 transition-colors"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={() => handleSubmitReply(comment.id)}
                      disabled={submitting || !replyText.trim()}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {submitting ? 'Posting...' : 'Post Reply'}
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Render Replies */}
      {comment.replies && comment.replies.length > 0 && (
        <div className="mt-4">
          {comment.replies.map((reply) => (
            <CommentItem key={reply.id} comment={reply} isReply={true} />
          ))}
        </div>
      )}
    </div>
  );

  if (loading) {
    return (
      <div className="flex justify-center items-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h3 className="text-2xl font-bold text-gray-800">Discussion ({comments.length})</h3>
      
      {/* New Comment Form */}
      {user ? (
        <div className="bg-white border rounded-lg p-6">
          <h4 className="text-lg font-semibold mb-4">Join the Discussion</h4>
          <form onSubmit={handleSubmitComment} className="space-y-4">
            <div className="flex items-start space-x-3">
              <img 
                src={user.picture || `https://ui-avatars.com/api/?name=${encodeURIComponent(user.name)}&background=0D8ABC&color=fff`}
                alt={user.name}
                className="w-10 h-10 rounded-full"
              />
              <div className="flex-1">
                <textarea
                  value={newComment}
                  onChange={(e) => setNewComment(e.target.value)}
                  placeholder="Share your thoughts about this motorcycle..."
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  maxLength={1000}
                />
                <div className="flex items-center justify-between mt-2">
                  <span className="text-sm text-gray-500">{newComment.length}/1000 characters</span>
                  <button
                    type="submit"
                    disabled={submitting || !newComment.trim()}
                    className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {submitting ? 'Posting...' : 'Post Comment'}
                  </button>
                </div>
              </div>
            </div>
          </form>
        </div>
      ) : (
        <div className="bg-gray-50 border rounded-lg p-6 text-center">
          <p className="text-gray-600 mb-4">Please login to join the discussion</p>
          <AuthButton />
        </div>
      )}

      {/* Comments List */}
      <div className="space-y-4">
        {comments.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            No comments yet. Be the first to start the discussion!
          </div>
        ) : (
          comments.map((comment) => (
            <CommentItem key={comment.id} comment={comment} />
          ))
        )}
      </div>
    </div>
  );
};

// Authentication Modal Component
const AuthModal = ({ isOpen, onClose }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register, login, loginWithGoogle } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      let result;
      if (isLogin) {
        result = await login(formData.email, formData.password);
      } else {
        result = await register(formData.email, formData.password, formData.name);
      }

      if (result.success) {
        onClose();
        setFormData({ email: '', password: '', name: '' });
      } else {
        setError(result.error);
      }
    } catch (err) {
      setError('An unexpected error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = async () => {
    setError('');
    setLoading(true);
    
    try {
      await loginWithGoogle();
    } catch (err) {
      setError('Google login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-xl max-w-md w-full p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-800">
            {isLogin ? 'Login' : 'Register'}
          </h2>
          <button 
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-xl"
          >
            ×
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {!isLogin && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Name
              </label>
              <input
                type="text"
                required
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Enter your name"
              />
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <input
              type="email"
              required
              value={formData.email}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter your email"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Password
            </label>
            <input
              type="password"
              required
              value={formData.password}
              onChange={(e) => setFormData({...formData, password: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter your password"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
          >
            {loading ? 'Please wait...' : (isLogin ? 'Login' : 'Register')}
          </button>
        </form>

        <div className="mt-4">
          <div className="text-center text-gray-500 mb-4">or</div>
          
          <button
            onClick={handleGoogleLogin}
            className="w-full bg-red-600 text-white py-2 px-4 rounded-lg hover:bg-red-700 transition-colors flex items-center justify-center space-x-2"
          >
            <span>🚀</span>
            <span>Continue with Google</span>
          </button>
        </div>

        <div className="mt-6 text-center">
          <button
            onClick={() => {
              setIsLogin(!isLogin);
              setError('');
              setFormData({ email: '', password: '', name: '' });
            }}
            className="text-blue-600 hover:text-blue-800 text-sm"
          >
            {isLogin ? "Don't have an account? Register" : "Already have an account? Login"}
          </button>
        </div>
      </div>
    </div>
  );
};
// Authentication Components
const AuthButton = () => {
  const { user, logout } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);

  if (user) {
    return (
      <div className="flex items-center space-x-3">
        <img src={user.picture} alt={user.name} className="w-8 h-8 rounded-full" />
        <span className="text-gray-700">{user.name}</span>
        <button
          onClick={logout}
          className="text-red-600 hover:text-red-800 text-sm"
        >
          Logout
        </button>
      </div>
    );
  }

  return (
    <>
      <button
        onClick={() => setShowAuthModal(true)}
        className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
      >
        Login / Sign Up
      </button>
      <AuthModal 
        isOpen={showAuthModal} 
        onClose={() => setShowAuthModal(false)} 
      />
    </>
  );
};

// Profile Page Component
const ProfilePage = () => {
  const { user } = useAuth();
  const [favorites, setFavorites] = useState([]);

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.hash.substring(1));
    const sessionId = urlParams.get('session_id');
    
    if (sessionId) {
      handleAuthCallback(sessionId);
    }
  }, []);

  useEffect(() => {
    if (user) {
      fetchFavorites();
    }
  }, [user]);

  const handleAuthCallback = async (sessionId) => {
    try {
      const response = await fetch('https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data', {
        headers: { 'X-Session-ID': sessionId }
      });
      const userData = await response.json();

      await axios.post(`${API}/auth/profile`, userData);
      
      localStorage.setItem('session_id', userData.session_token);
      
      window.location.href = '/';
    } catch (error) {
      console.error('Auth callback error:', error);
    }
  };

  const fetchFavorites = async () => {
    try {
      const sessionId = localStorage.getItem('session_id');
      const response = await axios.get(`${API}/motorcycles/favorites`, {
        headers: { 'X-Session-ID': sessionId }
      });
      setFavorites(response.data);
    } catch (error) {
      console.error('Error fetching favorites:', error);
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-4">Please login to view your profile</h2>
          <AuthButton />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
          <div className="flex items-center space-x-4 mb-6">
            <img src={user.picture} alt={user.name} className="w-16 h-16 rounded-full" />
            <div>
              <h1 className="text-2xl font-bold text-gray-800">{user.name}</h1>
              <p className="text-gray-600">{user.email}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-8">
          <h2 className="text-xl font-bold text-gray-800 mb-6">
            Your Favorite Motorcycles ({favorites.length})
          </h2>
          
          {favorites.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {favorites.map((motorcycle) => (
                <MotorcycleCard
                  key={motorcycle.id}
                  motorcycle={motorcycle}
                  onClick={() => {}}
                  showFavoriteButton={false}
                />
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">
              No favorite motorcycles yet. Start exploring and add some favorites!
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

// Carousel Images for Homepage Banner
const CAROUSEL_IMAGES = [
  {
    url: "https://images.unsplash.com/photo-1591637333184-19aa84b3e01f?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzl8MHwxfHNlYXJjaHwxfHxtb3RvcmN5Y2xlfGVufDB8fHx8MTc1MzgxMjgyMXww&ixlib=rb-4.1.0&q=85",
    title: "Performance Unleashed",
    subtitle: "Discover the latest sport motorcycles"
  },
  {
    url: "https://images.unsplash.com/photo-1558981806-ec527fa84c39?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzl8MHwxfHNlYXJjaHwyfHxtb3RvcmN5Y2xlfGVufDB8fHx8MTc1MzgxMjgyMXww&ixlib=rb-4.1.0&q=85",
    title: "Freedom on Two Wheels", 
    subtitle: "Experience the open road"
  },
  {
    url: "https://images.unsplash.com/photo-1531327431456-837da4b1d562?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzl8MHwxfHNlYXJjaHwzfHxtb3RvcmN5Y2xlfGVufDB8fHx8MTc1MzgxMjgyMXww&ixlib=rb-4.1.0&q=85",
    title: "Premium Engineering",
    subtitle: "Luxury meets performance"
  },
  {
    url: "https://images.unsplash.com/photo-1558981403-c5f9899a28bc?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzl8MHwxfHNlYXJjaHw0fHxtb3RvcmN5Y2xlfGVufDB8fHx8MTc1MzgxMjgyMXww&ixlib=rb-4.1.0&q=85",
    title: "Adventure Awaits",
    subtitle: "Built for every journey"
  },
  {
    url: "https://images.pexels.com/photos/1416169/pexels-photo-1416169.jpeg",
    title: "Explore Without Limits",
    subtitle: "Your next adventure starts here"
  }
];

// Hero Carousel Component
const HeroCarousel = ({ onViewChange }) => {
  const [currentSlide, setCurrentSlide] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % CAROUSEL_IMAGES.length);
    }, 5000); // Change slide every 5 seconds

    return () => clearInterval(timer);
  }, []);

  const goToSlide = (index) => {
    setCurrentSlide(index);
  };

  const goToPrevious = () => {
    setCurrentSlide((prev) => (prev - 1 + CAROUSEL_IMAGES.length) % CAROUSEL_IMAGES.length);
  };

  const goToNext = () => {
    setCurrentSlide((prev) => (prev + 1) % CAROUSEL_IMAGES.length);
  };

  return (
    <div className="relative h-96 md:h-[500px] overflow-hidden rounded-2xl shadow-2xl">
      {/* Image Slides */}
      {CAROUSEL_IMAGES.map((image, index) => (
        <div
          key={index}
          className={`absolute inset-0 transition-opacity duration-1000 ease-in-out ${
            index === currentSlide ? 'opacity-100' : 'opacity-0'
          }`}
        >
          <img
            src={image.url}
            alt={image.title}
            className="w-full h-full object-cover"
          />
          {/* Gradient Overlay */}
          <div className="absolute inset-0 bg-gradient-to-r from-black/60 via-black/30 to-transparent"></div>
          
          {/* Content Overlay */}
          <div className="absolute inset-0 flex flex-col justify-center px-8 md:px-16">
            <div className="text-white max-w-2xl">
              <h1 className="text-4xl md:text-6xl font-bold mb-4 leading-tight">
                {image.title}
              </h1>
              <p className="text-xl md:text-2xl mb-8 opacity-90">
                {image.subtitle}
              </p>
              <div className="flex space-x-4">
                <button 
                  onClick={() => onViewChange('browse')}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg font-semibold transition-colors duration-300 shadow-lg"
                >
                  Explore Motorcycles
                </button>
                <button 
                  onClick={() => onViewChange('browse')}
                  className="border-2 border-white text-white hover:bg-white hover:text-gray-900 px-8 py-3 rounded-lg font-semibold transition-all duration-300"
                >
                  View Brands
                </button>
              </div>
            </div>
          </div>
        </div>
      ))}

      {/* Navigation Arrows */}
      <button
        onClick={goToPrevious}
        className="absolute left-4 top-1/2 transform -translate-y-1/2 bg-white/20 hover:bg-white/30 text-white p-3 rounded-full transition-all duration-300 backdrop-blur-sm"
      >
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
        </svg>
      </button>
      <button
        onClick={goToNext}
        className="absolute right-4 top-1/2 transform -translate-y-1/2 bg-white/20 hover:bg-white/30 text-white p-3 rounded-full transition-all duration-300 backdrop-blur-sm"
      >
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
      </button>

      {/* Slide Indicators */}
      <div className="absolute bottom-6 left-1/2 transform -translate-x-1/2 flex space-x-2">
        {CAROUSEL_IMAGES.map((_, index) => (
          <button
            key={index}
            onClick={() => goToSlide(index)}
            className={`w-3 h-3 rounded-full transition-all duration-300 ${
              index === currentSlide 
                ? 'bg-white scale-125' 
                : 'bg-white/50 hover:bg-white/75'
            }`}
          />
        ))}
      </div>
    </div>
  );
};

// User Activity Analytics Page
const UserActivityPage = ({ onBack }) => {
  const { user } = useAuth();
  const [activityStats, setActivityStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      fetchActivityStats();
    }
  }, [user]);

  const fetchActivityStats = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('auth_token');
      const sessionId = localStorage.getItem('session_id');
      
      const headers = {};
      if (token) {
        headers.Authorization = `Bearer ${token}`;
      } else if (sessionId) {
        headers['X-Session-ID'] = sessionId;
      }

      const response = await axios.get(`${API}/users/${user.id}/activity-stats`, { headers });
      setActivityStats(response.data);
    } catch (error) {
      console.error('Error fetching activity stats:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Login Required</h2>
          <p className="text-gray-600 mb-6">Please login to view your activity statistics</p>
          <AuthButton />
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const StatCard = ({ title, value, subtitle, icon, color = "blue" }) => (
    <div className="bg-white p-6 rounded-xl shadow-lg">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className={`text-3xl font-bold text-${color}-600`}>{value}</p>
          {subtitle && <p className="text-sm text-gray-500 mt-1">{subtitle}</p>}
        </div>
        <div className={`text-4xl opacity-20`}>{icon}</div>
      </div>
    </div>
  );

  const AchievementBadge = ({ achievement }) => (
    <div className="bg-white p-4 rounded-lg shadow border-l-4 border-yellow-400">
      <div className="flex items-center space-x-3">
        <span className="text-2xl">{achievement.icon}</span>
        <div>
          <h4 className="font-semibold text-gray-800">{achievement.title}</h4>
          <p className="text-sm text-gray-600">{achievement.description}</p>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <button
                onClick={onBack}
                className="flex items-center text-gray-600 hover:text-blue-600 transition-colors"
              >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
                Back to Home
              </button>
              <h1 className="text-2xl font-bold text-gray-800">My Activity Dashboard</h1>
            </div>
            <div className="flex items-center space-x-3">
              <img 
                src={user.picture || `https://ui-avatars.com/api/?name=${encodeURIComponent(user.name)}&background=0D8ABC&color=fff`}
                alt={user.name}
                className="w-10 h-10 rounded-full"
              />
              <span className="font-medium text-gray-800">{user.name}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activityStats && (
          <>
            {/* Main Statistics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <StatCard
                title="Motorcycles Favorited"
                value={activityStats.total_stats.favorites_count}
                icon="❤️"
                color="red"
              />
              <StatCard
                title="Ratings Given"
                value={activityStats.total_stats.ratings_given}
                icon="⭐"
                color="yellow"
              />
              <StatCard
                title="Comments Posted"
                value={activityStats.total_stats.comments_posted}
                icon="💬"
                color="green"
              />
              <StatCard
                title="Discussions Started"
                value={activityStats.total_stats.discussion_threads}
                icon="🚀"
                color="purple"
              />
            </div>

            {/* Engagement Score */}
            <div className="bg-white p-6 rounded-xl shadow-lg mb-8">
              <h3 className="text-xl font-bold text-gray-800 mb-4">Engagement Score</h3>
              <div className="flex items-center space-x-4">
                <div className="flex-1">
                  <div className="bg-gray-200 rounded-full h-4">
                    <div 
                      className="bg-gradient-to-r from-blue-500 to-purple-600 h-4 rounded-full transition-all duration-1000"
                      style={{ width: `${Math.min(100, activityStats.total_stats.engagement_score)}%` }}
                    ></div>
                  </div>
                </div>
                <span className="text-2xl font-bold text-blue-600">
                  {activityStats.total_stats.engagement_score}%
                </span>
              </div>
              <p className="text-sm text-gray-600 mt-2">
                Based on your interactions with motorcycles, ratings, and community participation
              </p>
            </div>

            {/* Recent Activity */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              <div className="bg-white p-6 rounded-xl shadow-lg">
                <h3 className="text-xl font-bold text-gray-800 mb-4">Recent Activity (30 Days)</h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">Comments Posted</span>
                    <span className="font-semibold text-blue-600">
                      {activityStats.recent_activity.comments_last_30_days}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">Ratings Given</span>
                    <span className="font-semibold text-blue-600">
                      {activityStats.recent_activity.ratings_last_30_days}
                    </span>
                  </div>
                </div>
              </div>

              <div className="bg-white p-6 rounded-xl shadow-lg">
                <h3 className="text-xl font-bold text-gray-800 mb-4">Favorite Manufacturers</h3>
                <div className="space-y-3">
                  {activityStats.preferences.top_manufacturers.length > 0 ? (
                    activityStats.preferences.top_manufacturers.map(([manufacturer, count], index) => (
                      <div key={manufacturer} className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <span className="text-sm font-medium text-gray-500">#{index + 1}</span>
                          <span className="text-gray-800">{manufacturer}</span>
                        </div>
                        <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-sm">
                          {count}
                        </span>
                      </div>
                    ))
                  ) : (
                    <p className="text-gray-500 text-sm">No favorites yet</p>
                  )}
                </div>
              </div>
            </div>

            {/* Rating Distribution */}
            {Object.keys(activityStats.preferences.rating_distribution).length > 0 && (
              <div className="bg-white p-6 rounded-xl shadow-lg mb-8">
                <h3 className="text-xl font-bold text-gray-800 mb-4">Your Rating Distribution</h3>
                <div className="grid grid-cols-5 gap-4">
                  {[1, 2, 3, 4, 5].map(star => (
                    <div key={star} className="text-center">
                      <div className="text-yellow-400 text-2xl mb-2">
                        {'⭐'.repeat(star)}
                      </div>
                      <div className="text-2xl font-bold text-gray-800">
                        {activityStats.preferences.rating_distribution[star] || 0}
                      </div>
                      <div className="text-sm text-gray-500">{star} stars</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Achievements */}
            {activityStats.achievements && activityStats.achievements.length > 0 && (
              <div className="bg-white p-6 rounded-xl shadow-lg">
                <h3 className="text-xl font-bold text-gray-800 mb-6">Achievements</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {activityStats.achievements.map((achievement, index) => (
                    <AchievementBadge key={index} achievement={achievement} />
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

// Enhanced Image Component with Error Handling
const MotorcycleImage = ({ src, alt, className, showPlaceholderOnError = true }) => {
  const [imgSrc, setImgSrc] = useState(src);
  const [hasError, setHasError] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  
  const placeholderImage = "https://images.unsplash.com/photo-1558980664-2cd663cf8dde?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1ODB8MHwxfHNlYXJjaHwxfHxtb3RvcmN5Y2xlfGVufDB8fHxibGFja19hbmRfd2hpdGV8MTc1MzgxMDQyNXww&ixlib=rb-4.1.0&q=85";
  
  const handleImageError = () => {
    if (showPlaceholderOnError && imgSrc !== placeholderImage) {
      setImgSrc(placeholderImage);
      setHasError(true);
    }
    setIsLoading(false);
  };
  
  const handleImageLoad = () => {
    setIsLoading(false);
  };
  
  useEffect(() => {
    setImgSrc(src);
    setHasError(false);
    setIsLoading(true);
  }, [src]);
  
  return (
    <div className="relative">
      {isLoading && (
        <div className={`${className} bg-gray-200 animate-pulse flex items-center justify-center`}>
          <span className="text-gray-400 text-sm">Loading...</span>
        </div>
      )}
      <img 
        src={imgSrc}
        alt={alt}
        className={`${className} ${isLoading ? 'hidden' : ''}`}
        onError={handleImageError}
        onLoad={handleImageLoad}
      />
      {hasError && (
        <div className="absolute top-2 right-2 bg-yellow-500 text-white px-2 py-1 rounded text-xs">
          Generic Image
        </div>
      )}
    </div>
  );
};

const MotorcycleCard = ({ motorcycle, onClick, showFavoriteButton = true }) => {
  const { user } = useAuth();
  const [isFavorite, setIsFavorite] = useState(false);
  const [isCheckingFavorite, setIsCheckingFavorite] = useState(false);

  // Check if motorcycle is in user's favorites when component mounts or user changes
  useEffect(() => {
    if (user && motorcycle.id) {
      checkIfFavorite();
    } else {
      setIsFavorite(false); // Reset if no user
    }
  }, [user, motorcycle.id]);

  const checkIfFavorite = async () => {
    if (!user) return;
    
    try {
      setIsCheckingFavorite(true);
      const token = localStorage.getItem('auth_token');
      const sessionId = localStorage.getItem('session_id');
      
      const headers = {};
      if (token) {
        headers.Authorization = `Bearer ${token}`;
      } else if (sessionId) {
        headers['X-Session-ID'] = sessionId;
      }

      const response = await axios.get(`${API}/motorcycles/favorites`, { headers });
      const favorites = response.data;
      const isInFavorites = favorites.some(fav => fav.id === motorcycle.id);
      setIsFavorite(isInFavorites);
    } catch (error) {
      console.error('Error checking favorite status:', error);
      setIsFavorite(false);
    } finally {
      setIsCheckingFavorite(false);
    }
  };

  const handleFavoriteToggle = async (e) => {
    e.stopPropagation();
    
    if (!user) {
      // Prompt user to login
      alert('Please login to add motorcycles to your favorites');
      return;
    }

    try {
      const token = localStorage.getItem('auth_token');
      const sessionId = localStorage.getItem('session_id');
      
      const headers = {};
      if (token) {
        headers.Authorization = `Bearer ${token}`;
      } else if (sessionId) {
        headers['X-Session-ID'] = sessionId;
      }

      if (isFavorite) {
        await axios.delete(`${API}/motorcycles/${motorcycle.id}/favorite`, { headers });
        setIsFavorite(false);
      } else {
        await axios.post(`${API}/motorcycles/${motorcycle.id}/favorite`, {}, { headers });
        setIsFavorite(true);
      }
    } catch (error) {
      console.error('Error toggling favorite:', error);
      alert('Error updating favorites. Please try again.');
    }
  };

  const handleCardClick = (e) => {
    e.preventDefault();
    console.log('Card clicked, motorcycle:', motorcycle);
    if (onClick && typeof onClick === 'function') {
      onClick(motorcycle);
    } else {
      console.error('onClick is not a function:', onClick);
    }
  };

  return (
    <div 
      className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 cursor-pointer transform hover:scale-105"
      onClick={handleCardClick}
    >
      <div className="relative">
        <MotorcycleImage 
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
        {showFavoriteButton && user && (
          <button
            onClick={handleFavoriteToggle}
            disabled={isCheckingFavorite}
            className={`absolute top-4 left-1/2 transform -translate-x-1/2 w-10 h-10 rounded-full flex items-center justify-center transition-colors ${
              isFavorite 
                ? 'bg-red-500 text-white' 
                : 'bg-white bg-opacity-90 text-gray-400 hover:text-red-500 hover:bg-opacity-100'
            } ${isCheckingFavorite ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            {isCheckingFavorite ? '...' : (isFavorite ? '❤️' : '🤍')}
          </button>
        )}
        {showFavoriteButton && !user && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              alert('Please login to add motorcycles to your favorites');
            }}
            className="absolute top-4 left-1/2 transform -translate-x-1/2 w-10 h-10 rounded-full flex items-center justify-center bg-white bg-opacity-90 text-gray-400 hover:text-red-500 hover:bg-opacity-100 transition-colors"
          >
            🤍
          </button>
        )}
      </div>
      <div className="p-6">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-xl font-bold text-gray-800">{motorcycle.manufacturer}</h3>
          <span className="text-sm bg-blue-100 text-blue-800 px-2 py-1 rounded-full">{motorcycle.category}</span>
        </div>
        <h4 className="text-lg text-gray-600 mb-3">{motorcycle.model}</h4>
        
        {motorcycle.average_rating > 0 && (
          <div className="flex items-center space-x-2 mb-3">
            <StarRating rating={Math.round(motorcycle.average_rating)} readOnly />
            <span className="text-sm text-gray-500">({motorcycle.total_ratings})</span>
          </div>
        )}
        
        {/* Technical Features Display */}
        <div className="grid grid-cols-2 gap-2 text-sm text-gray-600 mb-4">
          <div className="flex items-center justify-between">
            <span>Year:</span>
            <span className="font-medium">{motorcycle.year}</span>
          </div>
          <div className="flex items-center justify-between">
            <span>Engine:</span>
            <span className="font-medium">{motorcycle.displacement}cc</span>
          </div>
          <div className="flex items-center justify-between">
            <span>Power:</span>
            <span className="font-medium">{motorcycle.horsepower}hp</span>
          </div>
          <div className="flex items-center justify-between">
            <span>Mileage:</span>
            <span className="font-medium">{motorcycle.mileage_kmpl || 'N/A'} kmpl</span>
          </div>
          {motorcycle.top_speed && (
            <div className="flex items-center justify-between">
              <span>Top Speed:</span>
              <span className="font-medium">{motorcycle.top_speed} km/h</span>
            </div>
          )}
          {motorcycle.weight && (
            <div className="flex items-center justify-between">
              <span>Weight:</span>
              <span className="font-medium">{motorcycle.weight} kg</span>
            </div>
          )}
        </div>
        
        <div className="flex items-center justify-between">
          <span className="text-2xl font-bold text-green-600">${motorcycle.price_usd.toLocaleString()}</span>
          <button 
            onClick={handleCardClick}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            View Details
          </button>
        </div>
      </div>
    </div>
  );
};

const CategorySection = ({ category, onMotorcycleClick, onViewAllClick }) => (
  <div className="mb-12">
    <div className="flex items-center justify-between mb-6">
      <div>
        <h2 className="text-3xl font-bold text-gray-800">{category.category}</h2>
        <p className="text-gray-600">{category.count} motorcycles available</p>
      </div>
      <button 
        onClick={() => onViewAllClick(category.category)}
        className="text-blue-600 hover:text-blue-800 font-medium transition-colors"
      >
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

const MotorcycleDetail = ({ motorcycle, onClose }) => {
  const [activeTab, setActiveTab] = useState('overview');

  // Add keyboard escape functionality
  useEffect(() => {
    const handleEscape = (event) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };
    
    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [onClose]);

  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
      onClick={(e) => {
        // Close modal when clicking the backdrop (not the modal content)
        if (e.target === e.currentTarget) {
          onClose();
        }
      }}
    >
      <div className="bg-white rounded-xl max-w-6xl w-full max-h-screen overflow-y-auto"
        onClick={(e) => e.stopPropagation()} // Prevent closing when clicking modal content
      >
        <div className="relative">
          <img 
            src={motorcycle.image_url} 
            alt={`${motorcycle.manufacturer} ${motorcycle.model}`}
            className="w-full h-80 object-cover rounded-t-xl"
          />
          {/* Enhanced Close Button - More Visible */}
          <button 
            onClick={onClose}
            className="absolute top-4 right-4 bg-red-500 hover:bg-red-600 text-white w-12 h-12 rounded-full flex items-center justify-center font-bold text-xl shadow-lg border-2 border-white hover:scale-110 transition-all duration-200 z-10"
            title="Close"
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
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-3xl font-bold text-gray-800">{motorcycle.manufacturer} {motorcycle.model}</h2>
              <p className="text-lg text-gray-600">{motorcycle.year} • {motorcycle.category}</p>
            </div>
            <div className="text-right">
              <div className="text-3xl font-bold text-green-600">${motorcycle.price_usd.toLocaleString()}</div>
              <div className="text-sm text-gray-500">{motorcycle.availability}</div>
            </div>
          </div>
          
          {/* Tab Navigation */}
          <div className="border-b border-gray-200 mb-6">
            <nav className="flex space-x-8">
              {['overview', 'pricing', 'ratings', 'discussion'].map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`py-2 px-1 border-b-2 font-medium text-sm capitalize transition-colors ${
                    activeTab === tab
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
                >
                  {tab}
                </button>
              ))}
            </nav>
          </div>

          {/* Tab Content */}
          {activeTab === 'overview' && (
            <div>
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
                <h3 className="text-lg font-semibold mb-4 text-gray-800">Key Specialisations</h3>
                <div className="flex flex-wrap gap-2">
                  {motorcycle.specialisations?.map((feature, index) => (
                    <span key={index} className="bg-blue-600 text-white px-3 py-1 rounded-full text-sm">
                      {feature}
                    </span>
                  )) || <span className="text-gray-500">No specialisations available</span>}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'pricing' && (
            <VendorPricing motorcycle={motorcycle} />
          )}

          {activeTab === 'ratings' && (
            <RatingSection 
              motorcycle={motorcycle} 
              onRatingSubmit={() => {
                // Refresh motorcycle data to update ratings
              }} 
            />
          )}

          {activeTab === 'discussion' && (
            <DiscussionSection motorcycle={motorcycle} />
          )}
          
          {/* Secondary Back Button for better accessibility */}
          <div className="mt-8 pt-6 border-t border-gray-200 text-center">
            <button
              onClick={onClose}
              className="bg-gray-600 hover:bg-gray-700 text-white px-6 py-3 rounded-lg font-medium transition-colors duration-200 shadow-md hover:shadow-lg"
            >
              ← Back to Browse
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Pagination Component
const PaginationControls = ({ currentPage, totalPages, onPageChange, totalCount, limit }) => {
  const startItem = (currentPage - 1) * limit + 1;
  const endItem = Math.min(currentPage * limit, totalCount);

  if (totalPages <= 1) return null;

  return (
    <div className="flex items-center justify-between mt-8 p-4 bg-white rounded-lg shadow">
      <div className="text-sm text-gray-600">
        Showing {startItem}-{endItem} of {totalCount} motorcycles
      </div>
      
      <div className="flex items-center space-x-2">
        <button
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage === 1}
          className="px-4 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Previous
        </button>

        <div className="flex items-center space-x-1">
          {/* First page */}
          {currentPage > 3 && (
            <>
              <button
                onClick={() => onPageChange(1)}
                className="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
              >
                1
              </button>
              {currentPage > 4 && <span className="px-2 text-gray-500">...</span>}
            </>
          )}

          {/* Page numbers around current page */}
          {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
            let pageNum;
            if (totalPages <= 5) {
              pageNum = i + 1;
            } else if (currentPage <= 3) {
              pageNum = i + 1;
            } else if (currentPage >= totalPages - 2) {
              pageNum = totalPages - 4 + i;
            } else {
              pageNum = currentPage - 2 + i;
            }

            if (pageNum < 1 || pageNum > totalPages) return null;

            return (
              <button
                key={pageNum}
                onClick={() => onPageChange(pageNum)}
                className={`px-3 py-2 text-sm font-medium rounded-md ${
                  pageNum === currentPage
                    ? 'text-blue-600 bg-blue-50 border border-blue-300'
                    : 'text-gray-500 bg-white border border-gray-300 hover:bg-gray-50'
                }`}
              >
                {pageNum}
              </button>
            );
          })}

          {/* Last page */}
          {currentPage < totalPages - 2 && (
            <>
              {currentPage < totalPages - 3 && <span className="px-2 text-gray-500">...</span>}
              <button
                onClick={() => onPageChange(totalPages)}
                className="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
              >
                {totalPages}
              </button>
            </>
          )}
        </div>

        <button
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
          className="px-4 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Next
        </button>
      </div>
    </div>
  );
};

const FilterSidebar = ({ filters, onFilterChange, filterOptions, availableFeatures, isOpen, onToggle }) => (
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
        <label className="block text-sm font-medium text-gray-700 mb-2">Features</label>
        <select
          value={filters.features || ''}
          onChange={(e) => onFilterChange({ ...filters, features: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="">All Features</option>
          {availableFeatures?.map(feature => (
            <option key={feature} value={feature}>{feature}</option>
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

// Community Page Component (Rider Groups)
const CommunityPage = () => {
  const { user } = useContext(AuthContext);
  const [riderGroups, setRiderGroups] = useState([]);
  const [myGroups, setMyGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedType, setSelectedType] = useState('');
  const [createFormData, setCreateFormData] = useState({
    name: '',
    description: '',
    location: '',
    group_type: 'general',
    is_public: true,
    max_members: ''
  });

  // Fetch public rider groups
  const fetchRiderGroups = async () => {
    try {
      let url = `${API}/rider-groups?limit=20`;
      if (searchTerm) url += `&search=${encodeURIComponent(searchTerm)}`;
      if (selectedType) url += `&group_type=${selectedType}`;
      
      const response = await axios.get(url);
      setRiderGroups(response.data.rider_groups || []);
    } catch (error) {
      console.error('Error fetching rider groups:', error);
    }
  };

  // Fetch user's joined groups
  const fetchMyGroups = async () => {
    if (!user) return;
    
    try {
      const token = localStorage.getItem('auth_token');
      const sessionId = localStorage.getItem('session_id');
      
      const headers = {};
      if (token) {
        headers.Authorization = `Bearer ${token}`;
      } else if (sessionId) {
        headers['X-Session-ID'] = sessionId;
      }
      
      const response = await axios.get(`${API}/users/me/rider-groups`, { headers });
      setMyGroups(response.data.rider_groups || []);
    } catch (error) {
      console.error('Error fetching my groups:', error);
    }
  };

  // Create new rider group
  const handleCreateGroup = async (e) => {
    e.preventDefault();
    
    try {
      const token = localStorage.getItem('auth_token');
      const sessionId = localStorage.getItem('session_id');
      
      const headers = {};
      if (token) {
        headers.Authorization = `Bearer ${token}`;
      } else if (sessionId) {
        headers['X-Session-ID'] = sessionId;
      }
      
      const formDataCopy = { ...createFormData };
      if (!formDataCopy.max_members) formDataCopy.max_members = null;
      else formDataCopy.max_members = parseInt(formDataCopy.max_members);
      
      await axios.post(`${API}/rider-groups`, formDataCopy, { headers });
      
      // Reset form and refresh data
      setCreateFormData({
        name: '',
        description: '',
        location: '',
        group_type: 'general',
        is_public: true,
        max_members: ''
      });
      setShowCreateForm(false);
      
      await Promise.all([fetchRiderGroups(), fetchMyGroups()]);
      alert('Rider group created successfully!');
    } catch (error) {
      console.error('Error creating group:', error);
      alert('Error creating group. Please try again.');
    }
  };

  // Join a rider group
  const handleJoinGroup = async (groupId) => {
    if (!user) {
      alert('Please log in to join groups');
      return;
    }
    
    try {
      const token = localStorage.getItem('auth_token');
      const sessionId = localStorage.getItem('session_id');
      
      const headers = {};
      if (token) {
        headers.Authorization = `Bearer ${token}`;
      } else if (sessionId) {
        headers['X-Session-ID'] = sessionId;
      }
      
      await axios.post(`${API}/rider-groups/${groupId}/join`, {}, { headers });
      
      await Promise.all([fetchRiderGroups(), fetchMyGroups()]);
      alert('Successfully joined the group!');
    } catch (error) {
      console.error('Error joining group:', error);
      const message = error.response?.data?.detail || 'Error joining group. Please try again.';
      alert(message);
    }
  };

  // Leave a rider group
  const handleLeaveGroup = async (groupId) => {
    if (!confirm('Are you sure you want to leave this group?')) return;
    
    try {
      const token = localStorage.getItem('auth_token');
      const sessionId = localStorage.getItem('session_id');
      
      const headers = {};
      if (token) {
        headers.Authorization = `Bearer ${token}`;
      } else if (sessionId) {
        headers['X-Session-ID'] = sessionId;
      }
      
      await axios.post(`${API}/rider-groups/${groupId}/leave`, {}, { headers });
      
      await Promise.all([fetchRiderGroups(), fetchMyGroups()]);
      alert('Successfully left the group!');
    } catch (error) {
      console.error('Error leaving group:', error);
      alert('Error leaving group. Please try again.');
    }
  };

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([fetchRiderGroups(), fetchMyGroups()]);
      setLoading(false);
    };
    
    loadData();
  }, [user, searchTerm, selectedType]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading community...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-800">Rider Community</h1>
              <p className="text-gray-600 mt-2">Connect with fellow motorcycle enthusiasts</p>
            </div>
            {user && (
              <button
                onClick={() => setShowCreateForm(!showCreateForm)}
                className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium"
              >
                {showCreateForm ? 'Cancel' : 'Create Group'}
              </button>
            )}
          </div>

          {/* Filters */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
            <div>
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search groups..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <select
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">All Group Types</option>
                <option value="location">Location-based</option>
                <option value="brand">Brand/Model</option>
                <option value="riding_style">Riding Style</option>
                <option value="general">General</option>
              </select>
            </div>
          </div>
        </div>

        {/* Create Group Form */}
        {showCreateForm && user && (
          <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">Create New Rider Group</h2>
            <form onSubmit={handleCreateGroup} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Group Name</label>
                  <input
                    type="text"
                    value={createFormData.name}
                    onChange={(e) => setCreateFormData({...createFormData, name: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                    minLength={3}
                    maxLength={100}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Group Type</label>
                  <select
                    value={createFormData.group_type}
                    onChange={(e) => setCreateFormData({...createFormData, group_type: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  >
                    <option value="general">General</option>
                    <option value="location">Location-based</option>
                    <option value="brand">Brand/Model</option>
                    <option value="riding_style">Riding Style</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                <textarea
                  value={createFormData.description}
                  onChange={(e) => setCreateFormData({...createFormData, description: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  rows={4}
                  required
                  minLength={10}
                  maxLength={1000}
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Location (Optional)</label>
                  <input
                    type="text"
                    value={createFormData.location}
                    onChange={(e) => setCreateFormData({...createFormData, location: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="e.g., California, USA"
                    maxLength={200}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Max Members (Optional)</label>
                  <input
                    type="number"
                    value={createFormData.max_members}
                    onChange={(e) => setCreateFormData({...createFormData, max_members: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    min="2"
                    max="1000"
                  />
                </div>
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="is_public"
                  checked={createFormData.is_public}
                  onChange={(e) => setCreateFormData({...createFormData, is_public: e.target.checked})}
                  className="mr-2"
                />
                <label htmlFor="is_public" className="text-sm text-gray-700">Make this group public</label>
              </div>

              <div className="flex justify-end space-x-4">
                <button
                  type="button"
                  onClick={() => setShowCreateForm(false)}
                  className="bg-gray-200 text-gray-800 px-6 py-2 rounded-lg hover:bg-gray-300 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Create Group
                </button>
              </div>
            </form>
          </div>
        )}

        {/* My Groups */}
        {user && myGroups.length > 0 && (
          <div className="bg-white rounded-xl shadow-lg mb-8">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-bold text-gray-800">My Groups</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-6">
              {myGroups.map((group) => (
                <div key={group.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-lg font-bold text-gray-800">{group.name}</h3>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                      group.is_creator ? 'bg-purple-100 text-purple-800' :
                      group.user_role === 'admin' ? 'bg-blue-100 text-blue-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {group.is_creator ? 'CREATOR' : group.user_role.toUpperCase()}
                    </span>
                  </div>
                  <p className="text-gray-600 mb-3 text-sm">{group.description}</p>
                  <div className="flex items-center justify-between text-sm text-gray-500 mb-3">
                    <span>{group.member_count} members</span>
                    <span className="capitalize">{group.group_type.replace('_', ' ')}</span>
                  </div>
                  {group.location && (
                    <div className="text-sm text-gray-500 mb-3">📍 {group.location}</div>
                  )}
                  {!group.is_creator && (
                    <button
                      onClick={() => handleLeaveGroup(group.id)}
                      className="w-full bg-red-50 text-red-600 px-3 py-2 rounded-lg hover:bg-red-100 transition-colors text-sm font-medium"
                    >
                      Leave Group
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Public Groups */}
        <div className="bg-white rounded-xl shadow-lg">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-xl font-bold text-gray-800">Discover Groups</h2>
          </div>
          
          {riderGroups.length === 0 ? (
            <div className="p-8 text-center">
              <div className="text-gray-400 text-6xl mb-4">👥</div>
              <h3 className="text-lg font-medium text-gray-800 mb-2">No groups found</h3>
              <p className="text-gray-600 mb-4">Try adjusting your search or create the first group!</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-6">
              {riderGroups.map((group) => {
                const isMyGroup = myGroups.some(mg => mg.id === group.id);
                return (
                  <div key={group.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="text-lg font-bold text-gray-800">{group.name}</h3>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        group.group_type === 'location' ? 'bg-green-100 text-green-800' :
                        group.group_type === 'brand' ? 'bg-blue-100 text-blue-800' :
                        group.group_type === 'riding_style' ? 'bg-purple-100 text-purple-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {group.group_type.replace('_', ' ').toUpperCase()}
                      </span>
                    </div>
                    <p className="text-gray-600 mb-3 text-sm">{group.description}</p>
                    <div className="flex items-center justify-between text-sm text-gray-500 mb-3">
                      <span>{group.member_count} members</span>
                      {group.max_members && (
                        <span>Max: {group.max_members}</span>
                      )}
                    </div>
                    {group.location && (
                      <div className="text-sm text-gray-500 mb-3">📍 {group.location}</div>
                    )}
                    <div className="text-xs text-gray-400 mb-3">
                      Created {new Date(group.created_at).toLocaleDateString()}
                    </div>
                    
                    {user && !isMyGroup ? (
                      <button
                        onClick={() => handleJoinGroup(group.id)}
                        className="w-full bg-blue-600 text-white px-3 py-2 rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
                      >
                        Join Group
                      </button>
                    ) : isMyGroup ? (
                      <div className="w-full bg-green-50 text-green-600 px-3 py-2 rounded-lg text-center text-sm font-medium">
                        ✅ Already a Member
                      </div>
                    ) : (
                      <div className="w-full bg-gray-50 text-gray-500 px-3 py-2 rounded-lg text-center text-sm font-medium">
                        Login to Join
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Achievements Page Component
const AchievementsPage = () => {
  const { user } = useContext(AuthContext);
  const [achievements, setAchievements] = useState([]);
  const [userStats, setUserStats] = useState({});
  const [loading, setLoading] = useState(true);

  // Fetch user achievements and progress
  const fetchUserAchievements = async () => {
    if (!user) return;
    
    try {
      const token = localStorage.getItem('auth_token');
      const sessionId = localStorage.getItem('session_id');
      
      const headers = {};
      if (token) {
        headers.Authorization = `Bearer ${token}`;
      } else if (sessionId) {
        headers['X-Session-ID'] = sessionId;
      }
      
      const response = await axios.get(`${API}/users/me/achievements`, { headers });
      setAchievements(response.data.achievements || []);
      setUserStats(response.data.stats || {});
    } catch (error) {
      console.error('Error fetching achievements:', error);
    }
  };

  // Check for new achievements
  const checkAchievements = async () => {
    if (!user) return;
    
    try {
      const token = localStorage.getItem('auth_token');
      const sessionId = localStorage.getItem('session_id');
      
      const headers = {};
      if (token) {
        headers.Authorization = `Bearer ${token}`;
      } else if (sessionId) {
        headers['X-Session-ID'] = sessionId;
      }
      
      const response = await axios.post(`${API}/achievements/check`, {}, { headers });
      
      if (response.data.new_achievements && response.data.new_achievements.length > 0) {
        alert(`🎉 Congratulations! You earned ${response.data.new_achievements.length} new achievement(s)!`);
        await fetchUserAchievements(); // Refresh data
      }
    } catch (error) {
      console.error('Error checking achievements:', error);
    }
  };

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await fetchUserAchievements();
      setLoading(false);
    };
    
    if (user) {
      loadData();
    } else {
      setLoading(false);
    }
  }, [user]);

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Authentication Required</h2>
          <p className="text-gray-600 mb-6">Please log in to view your achievements.</p>
          <button
            onClick={() => {/* You'd trigger auth modal here */}}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Login / Sign Up
          </button>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading achievements...</p>
        </div>
      </div>
    );
  }

  // Group achievements by category
  const achievementsByCategory = achievements.reduce((acc, achievement) => {
    const category = achievement.category || 'general';
    if (!acc[category]) acc[category] = [];
    acc[category].push(achievement);
    return acc;
  }, {});

  const categories = {
    social: { name: 'Social', icon: '👥', color: 'blue' },
    collection: { name: 'Collection', icon: '🏍️', color: 'green' },
    activity: { name: 'Activity', icon: '⚡', color: 'purple' },
    general: { name: 'General', icon: '🎯', color: 'gray' }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-800">Your Achievements</h1>
              <p className="text-gray-600 mt-2">Track your progress and unlock rewards</p>
            </div>
            <button
              onClick={checkAchievements}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              Check for New Achievements
            </button>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
            <div className="bg-blue-50 p-4 rounded-lg text-center">
              <div className="text-2xl font-bold text-blue-600">{userStats.completed_count || 0}</div>
              <div className="text-sm text-gray-600">Completed</div>
            </div>
            <div className="bg-green-50 p-4 rounded-lg text-center">
              <div className="text-2xl font-bold text-green-600">{userStats.total_achievements || 0}</div>
              <div className="text-sm text-gray-600">Total Available</div>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg text-center">
              <div className="text-2xl font-bold text-purple-600">{userStats.completion_rate || 0}%</div>
              <div className="text-sm text-gray-600">Completion Rate</div>
            </div>
            <div className="bg-yellow-50 p-4 rounded-lg text-center">
              <div className="text-2xl font-bold text-yellow-600">{userStats.total_points || 0}</div>
              <div className="text-sm text-gray-600">Points Earned</div>
            </div>
          </div>
        </div>

        {/* Achievements by Category */}
        {Object.entries(achievementsByCategory).map(([categoryKey, categoryAchievements]) => {
          const category = categories[categoryKey] || categories.general;
          
          return (
            <div key={categoryKey} className="bg-white rounded-xl shadow-lg mb-8">
              <div className="p-6 border-b border-gray-200">
                <h2 className="text-xl font-bold text-gray-800 flex items-center">
                  <span className="mr-2 text-2xl">{category.icon}</span>
                  {category.name} Achievements
                </h2>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-6">
                {categoryAchievements.map((achievement) => (
                  <div key={achievement.id} className={`border-2 rounded-lg p-4 transition-all ${
                    achievement.completed 
                      ? 'border-green-200 bg-green-50' 
                      : 'border-gray-200 bg-white hover:shadow-md'
                  }`}>
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-3xl">{achievement.icon}</span>
                      <div className="flex items-center space-x-2">
                        <span className="text-sm text-gray-500">{achievement.points}pts</span>
                        {achievement.completed && (
                          <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-medium">
                            ✅ COMPLETED
                          </span>
                        )}
                      </div>
                    </div>
                    
                    <h3 className="text-lg font-bold text-gray-800 mb-2">{achievement.name}</h3>
                    <p className="text-gray-600 text-sm mb-4">{achievement.description}</p>
                    
                    {/* Progress Bar */}
                    <div className="mb-3">
                      <div className="flex justify-between text-sm text-gray-500 mb-1">
                        <span>Progress</span>
                        <span>{achievement.progress || 0} / {achievement.requirement_value}</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full transition-all ${
                            achievement.completed ? 'bg-green-500' : 'bg-blue-500'
                          }`}
                          style={{ 
                            width: `${Math.min(100, ((achievement.progress || 0) / achievement.requirement_value) * 100)}%` 
                          }}
                        ></div>
                      </div>
                    </div>
                    
                    {achievement.completed && achievement.earned_at && (
                      <div className="text-xs text-green-600 font-medium">
                        Completed {new Date(achievement.earned_at).toLocaleDateString()}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

// Virtual Garage Page Component
const VirtualGaragePage = () => {
  const { user } = useContext(AuthContext);
  const [garageItems, setGarageItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [stats, setStats] = useState({});
  const [priceAlerts, setPriceAlerts] = useState([]);
  const [searchResults, setSearchResults] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedMotorcycle, setSelectedMotorcycle] = useState(null);
  const [addFormData, setAddFormData] = useState({
    motorcycle_id: '',
    status: 'owned',
    purchase_date: '',
    purchase_price: '',
    current_mileage: '',
    modifications: [],
    notes: '',
    is_public: true
  });

  // Fetch garage items
  const fetchGarageItems = async () => {
    if (!user) return;
    
    try {
      const token = localStorage.getItem('auth_token');
      const sessionId = localStorage.getItem('session_id');
      
      const headers = {};
      if (token) {
        headers.Authorization = `Bearer ${token}`;
      } else if (sessionId) {
        headers['X-Session-ID'] = sessionId;
      }
      
      const response = await axios.get(`${API}/garage`, { headers });
      setGarageItems(response.data.garage_items || []);
    } catch (error) {
      console.error('Error fetching garage items:', error);
    }
  };

  // Fetch garage stats
  const fetchGarageStats = async () => {
    if (!user) return;
    
    try {
      const token = localStorage.getItem('auth_token');
      const sessionId = localStorage.getItem('session_id');
      
      const headers = {};
      if (token) {
        headers.Authorization = `Bearer ${token}`;
      } else if (sessionId) {
        headers['X-Session-ID'] = sessionId;
      }
      
      const response = await axios.get(`${API}/garage/stats`, { headers });
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching garage stats:', error);
    }
  };

  // Fetch price alerts
  const fetchPriceAlerts = async () => {
    if (!user) return;
    
    try {
      const token = localStorage.getItem('auth_token');
      const sessionId = localStorage.getItem('session_id');
      
      const headers = {};
      if (token) {
        headers.Authorization = `Bearer ${token}`;
      } else if (sessionId) {
        headers['X-Session-ID'] = sessionId;
      }
      
      const response = await axios.get(`${API}/price-alerts`, { headers });
      setPriceAlerts(response.data.price_alerts || []);
    } catch (error) {
      console.error('Error fetching price alerts:', error);
    }
  };

  // Search motorcycles for adding to garage
  const searchMotorcycles = async (term) => {
    if (!term || term.length < 2) {
      setSearchResults([]);
      return;
    }
    
    try {
      const response = await axios.get(`${API}/motorcycles?search=${encodeURIComponent(term)}&limit=10`);
      setSearchResults(response.data.motorcycles || []);
    } catch (error) {
      console.error('Error searching motorcycles:', error);
    }
  };

  // Add motorcycle to garage
  const handleAddToGarage = async (e) => {
    e.preventDefault();
    
    try {
      const token = localStorage.getItem('auth_token');
      const sessionId = localStorage.getItem('session_id');
      
      const headers = {};
      if (token) {
        headers.Authorization = `Bearer ${token}`;
      } else if (sessionId) {
        headers['X-Session-ID'] = sessionId;
      }
      
      const formDataCopy = { ...addFormData };
      
      // Convert empty strings to null for optional numeric fields
      if (!formDataCopy.purchase_price) formDataCopy.purchase_price = null;
      if (!formDataCopy.current_mileage) formDataCopy.current_mileage = null;
      if (!formDataCopy.purchase_date) formDataCopy.purchase_date = null;
      
      await axios.post(`${API}/garage`, formDataCopy, { headers });
      
      // Reset form and refresh data
      setAddFormData({
        motorcycle_id: '',
        status: 'owned',
        purchase_date: '',
        purchase_price: '',
        current_mileage: '',
        modifications: [],
        notes: '',
        is_public: true
      });
      setShowAddForm(false);
      setSelectedMotorcycle(null);
      setSearchResults([]);
      setSearchTerm('');
      
      // Refresh garage data
      await Promise.all([fetchGarageItems(), fetchGarageStats()]);
      
      alert('Added to garage successfully!');
    } catch (error) {
      console.error('Error adding to garage:', error);
      alert('Error adding to garage. Please try again.');
    }
  };

  // Remove from garage
  const handleRemoveFromGarage = async (itemId) => {
    if (!confirm('Are you sure you want to remove this from your garage?')) return;
    
    try {
      const token = localStorage.getItem('auth_token');
      const sessionId = localStorage.getItem('session_id');
      
      const headers = {};
      if (token) {
        headers.Authorization = `Bearer ${token}`;
      } else if (sessionId) {
        headers['X-Session-ID'] = sessionId;
      }
      
      await axios.delete(`${API}/garage/${itemId}`, { headers });
      
      // Refresh garage data
      await Promise.all([fetchGarageItems(), fetchGarageStats()]);
      
      alert('Removed from garage successfully!');
    } catch (error) {
      console.error('Error removing from garage:', error);
      alert('Error removing from garage. Please try again.');
    }
  };

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([fetchGarageItems(), fetchGarageStats(), fetchPriceAlerts()]);
      setLoading(false);
    };
    
    if (user) {
      loadData();
    } else {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    const debounceTimer = setTimeout(() => {
      searchMotorcycles(searchTerm);
    }, 300);
    
    return () => clearTimeout(debounceTimer);
  }, [searchTerm]);

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Authentication Required</h2>
          <p className="text-gray-600 mb-6">Please log in to access your virtual garage.</p>
          <button
            onClick={() => {/* You'd trigger auth modal here */}}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Login / Sign Up
          </button>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your garage...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-800">My Virtual Garage</h1>
              <p className="text-gray-600 mt-2">Manage your motorcycle collection and wishlist</p>
            </div>
            <button
              onClick={() => setShowAddForm(!showAddForm)}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              {showAddForm ? 'Cancel' : 'Add Motorcycle'}
            </button>
          </div>

          {/* Stats */}
          {stats.total_items > 0 && (
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mt-6">
              <div className="bg-blue-50 p-4 rounded-lg text-center">
                <div className="text-2xl font-bold text-blue-600">{stats.total_items}</div>
                <div className="text-sm text-gray-600">Total Items</div>
              </div>
              <div className="bg-green-50 p-4 rounded-lg text-center">
                <div className="text-2xl font-bold text-green-600">{stats.by_status.owned}</div>
                <div className="text-sm text-gray-600">Owned</div>
              </div>
              <div className="bg-yellow-50 p-4 rounded-lg text-center">
                <div className="text-2xl font-bold text-yellow-600">{stats.by_status.wishlist}</div>
                <div className="text-sm text-gray-600">Wishlist</div>
              </div>
              <div className="bg-purple-50 p-4 rounded-lg text-center">
                <div className="text-2xl font-bold text-purple-600">{stats.by_status.test_ridden}</div>
                <div className="text-sm text-gray-600">Test Ridden</div>
              </div>
              <div className="bg-red-50 p-4 rounded-lg text-center">
                <div className="text-2xl font-bold text-red-600">${stats.estimated_value?.toLocaleString() || 0}</div>
                <div className="text-sm text-gray-600">Est. Value</div>
              </div>
            </div>
          )}
        </div>

        {/* Add Motorcycle Form */}
        {showAddForm && (
          <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">Add Motorcycle to Garage</h2>
            
            {/* Search for motorcycle */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">Search Motorcycle</label>
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Type to search motorcycles..."
              />
              
              {/* Search results */}
              {searchResults.length > 0 && (
                <div className="mt-2 border border-gray-300 rounded-lg max-h-48 overflow-y-auto">
                  {searchResults.map((motorcycle) => (
                    <div
                      key={motorcycle.id}
                      onClick={() => {
                        setSelectedMotorcycle(motorcycle);
                        setAddFormData({...addFormData, motorcycle_id: motorcycle.id});
                        setSearchResults([]);
                        setSearchTerm(`${motorcycle.manufacturer} ${motorcycle.model} (${motorcycle.year})`);
                      }}
                      className="p-3 hover:bg-gray-50 cursor-pointer border-b border-gray-200 last:border-b-0"
                    >
                      <div className="font-medium">{motorcycle.manufacturer} {motorcycle.model}</div>
                      <div className="text-sm text-gray-600">{motorcycle.year} • {motorcycle.category} • ${motorcycle.price_usd?.toLocaleString()}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {selectedMotorcycle && (
              <form onSubmit={handleAddToGarage} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
                    <select
                      value={addFormData.status}
                      onChange={(e) => setAddFormData({...addFormData, status: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      required
                    >
                      <option value="owned">Owned</option>
                      <option value="wishlist">Wishlist</option>
                      <option value="previously_owned">Previously Owned</option>
                      <option value="test_ridden">Test Ridden</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Purchase Date (Optional)</label>
                    <input
                      type="date"
                      value={addFormData.purchase_date}
                      onChange={(e) => setAddFormData({...addFormData, purchase_date: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Purchase Price (USD) (Optional)</label>
                    <input
                      type="number"
                      value={addFormData.purchase_price}
                      onChange={(e) => setAddFormData({...addFormData, purchase_price: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      min="0"
                      step="0.01"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Current Mileage (Optional)</label>
                    <input
                      type="number"
                      value={addFormData.current_mileage}
                      onChange={(e) => setAddFormData({...addFormData, current_mileage: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      min="0"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Notes (Optional)</label>
                  <textarea
                    value={addFormData.notes}
                    onChange={(e) => setAddFormData({...addFormData, notes: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    rows={3}
                    placeholder="Any notes about this motorcycle..."
                    maxLength={1000}
                  />
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="is_public"
                    checked={addFormData.is_public}
                    onChange={(e) => setAddFormData({...addFormData, is_public: e.target.checked})}
                    className="mr-2"
                  />
                  <label htmlFor="is_public" className="text-sm text-gray-700">Make this visible in my public garage</label>
                </div>

                <div className="flex justify-end space-x-4">
                  <button
                    type="button"
                    onClick={() => {setShowAddForm(false); setSelectedMotorcycle(null);}}
                    className="bg-gray-200 text-gray-800 px-6 py-2 rounded-lg hover:bg-gray-300 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Add to Garage
                  </button>
                </div>
              </form>
            )}
          </div>
        )}

        {/* Garage Items */}
        <div className="bg-white rounded-xl shadow-lg">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-xl font-bold text-gray-800">Your Motorcycle Collection</h2>
          </div>
          
          {garageItems.length === 0 ? (
            <div className="p-8 text-center">
              <div className="text-gray-400 text-6xl mb-4">🏍️</div>
              <h3 className="text-lg font-medium text-gray-800 mb-2">No motorcycles in your garage yet</h3>
              <p className="text-gray-600 mb-4">Start building your virtual collection!</p>
              <button
                onClick={() => setShowAddForm(true)}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
              >
                Add Your First Motorcycle
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-6">
              {garageItems.map((item) => (
                <div key={item.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                  {item.motorcycle && (
                    <>
                      <img
                        src={item.motorcycle.image_url}
                        alt={`${item.motorcycle.manufacturer} ${item.motorcycle.model}`}
                        className="w-full h-48 object-cover rounded-lg mb-4"
                      />
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="text-lg font-bold text-gray-800">
                          {item.motorcycle.manufacturer} {item.motorcycle.model}
                        </h3>
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                          item.status === 'owned' ? 'bg-green-100 text-green-800' :
                          item.status === 'wishlist' ? 'bg-blue-100 text-blue-800' :
                          item.status === 'previously_owned' ? 'bg-gray-100 text-gray-800' :
                          'bg-yellow-100 text-yellow-800'
                        }`}>
                          {item.status.replace('_', ' ').toUpperCase()}
                        </span>
                      </div>
                      <p className="text-gray-600 mb-3">{item.motorcycle.year} • {item.motorcycle.category}</p>
                      
                      {item.purchase_price && (
                        <div className="text-sm text-gray-600 mb-1">
                          Purchase Price: ${item.purchase_price.toLocaleString()}
                        </div>
                      )}
                      
                      {item.current_mileage && (
                        <div className="text-sm text-gray-600 mb-1">
                          Mileage: {item.current_mileage.toLocaleString()} miles
                        </div>
                      )}
                      
                      {item.notes && (
                        <div className="text-sm text-gray-600 mb-3 italic">
                          "{item.notes}"
                        </div>
                      )}
                      
                      <div className="flex justify-between items-center mt-4">
                        <span className="text-xs text-gray-500">
                          Added {new Date(item.created_at).toLocaleDateString()}
                        </span>
                        <button
                          onClick={() => handleRemoveFromGarage(item.id)}
                          className="text-red-600 hover:text-red-800 text-sm font-medium"
                        >
                          Remove
                        </button>
                      </div>
                    </>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// User Requests Page Component
const UserRequestsPage = () => {
  const { user } = useContext(AuthContext);
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showSubmissionForm, setShowSubmissionForm] = useState(false);
  const [stats, setStats] = useState({});
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    request_type: 'feature_request',
    priority: 'medium',
    category: '',
    motorcycle_related: ''
  });

  // Fetch user requests
  const fetchRequests = async () => {
    if (!user) return;
    
    try {
      const token = localStorage.getItem('auth_token');
      const sessionId = localStorage.getItem('session_id');
      
      const headers = {};
      if (token) {
        headers.Authorization = `Bearer ${token}`;
      } else if (sessionId) {
        headers['X-Session-ID'] = sessionId;
      }
      
      const response = await axios.get(`${API}/requests`, { headers });
      setRequests(response.data.requests || []);
    } catch (error) {
      console.error('Error fetching requests:', error);
    }
  };

  // Fetch user stats
  const fetchStats = async () => {
    if (!user) return;
    
    try {
      const token = localStorage.getItem('auth_token');
      const sessionId = localStorage.getItem('session_id');
      
      const headers = {};
      if (token) {
        headers.Authorization = `Bearer ${token}`;
      } else if (sessionId) {
        headers['X-Session-ID'] = sessionId;
      }
      
      const response = await axios.get(`${API}/requests/stats`, { headers });
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  // Submit new request
  const handleSubmitRequest = async (e) => {
    e.preventDefault();
    
    try {
      const token = localStorage.getItem('auth_token');
      const sessionId = localStorage.getItem('session_id');
      
      const headers = {};
      if (token) {
        headers.Authorization = `Bearer ${token}`;
      } else if (sessionId) {
        headers['X-Session-ID'] = sessionId;
      }
      
      await axios.post(`${API}/requests`, formData, { headers });
      
      // Reset form and refresh data
      setFormData({
        title: '',
        description: '',
        request_type: 'feature_request',
        priority: 'medium',
        category: '',
        motorcycle_related: ''
      });
      setShowSubmissionForm(false);
      
      // Refresh requests and stats
      await Promise.all([fetchRequests(), fetchStats()]);
      
      alert('Request submitted successfully!');
    } catch (error) {
      console.error('Error submitting request:', error);
      alert('Error submitting request. Please try again.');
    }
  };

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([fetchRequests(), fetchStats()]);
      setLoading(false);
    };
    
    if (user) {
      loadData();
    } else {
      setLoading(false);
    }
  }, [user]);

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Authentication Required</h2>
          <p className="text-gray-600 mb-6">Please log in to submit and view your requests.</p>
          <button
            onClick={() => {/* You'd trigger auth modal here */}}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Login / Sign Up
          </button>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your requests...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-800">Your Requests</h1>
              <p className="text-gray-600 mt-2">Submit feedback, feature requests, and bug reports</p>
            </div>
            <button
              onClick={() => setShowSubmissionForm(!showSubmissionForm)}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              {showSubmissionForm ? 'Cancel' : 'Submit New Request'}
            </button>
          </div>

          {/* Stats */}
          {stats.total_requests > 0 && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
              <div className="bg-blue-50 p-4 rounded-lg text-center">
                <div className="text-2xl font-bold text-blue-600">{stats.total_requests}</div>
                <div className="text-sm text-gray-600">Total Requests</div>
              </div>
              <div className="bg-yellow-50 p-4 rounded-lg text-center">
                <div className="text-2xl font-bold text-yellow-600">{stats.by_status.pending}</div>
                <div className="text-sm text-gray-600">Pending</div>
              </div>
              <div className="bg-green-50 p-4 rounded-lg text-center">
                <div className="text-2xl font-bold text-green-600">{stats.by_status.resolved}</div>
                <div className="text-sm text-gray-600">Resolved</div>
              </div>
              <div className="bg-purple-50 p-4 rounded-lg text-center">
                <div className="text-2xl font-bold text-purple-600">{stats.response_rate}%</div>
                <div className="text-sm text-gray-600">Response Rate</div>
              </div>
            </div>
          )}
        </div>

        {/* Submission Form */}
        {showSubmissionForm && (
          <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">Submit New Request</h2>
            <form onSubmit={handleSubmitRequest} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Request Type</label>
                  <select
                    value={formData.request_type}
                    onChange={(e) => setFormData({...formData, request_type: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  >
                    <option value="feature_request">Feature Request</option>
                    <option value="bug_report">Bug Report</option>
                    <option value="motorcycle_addition">Motorcycle Addition</option>
                    <option value="general_feedback">General Feedback</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Priority</label>
                  <select
                    value={formData.priority}
                    onChange={(e) => setFormData({...formData, priority: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="critical">Critical</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Title</label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({...formData, title: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Brief title for your request..."
                  required
                  minLength={5}
                  maxLength={200}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  rows={6}
                  placeholder="Detailed description of your request..."
                  required
                  minLength={10}
                  maxLength={2000}
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Category (Optional)</label>
                  <input
                    type="text"
                    value={formData.category}
                    onChange={(e) => setFormData({...formData, category: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="e.g., Search, Filters, UI/UX..."
                    maxLength={100}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Related Motorcycle ID (Optional)</label>
                  <input
                    type="text"
                    value={formData.motorcycle_related}
                    onChange={(e) => setFormData({...formData, motorcycle_related: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="If related to specific motorcycle..."
                  />
                </div>
              </div>

              <div className="flex justify-end space-x-4">
                <button
                  type="button"
                  onClick={() => setShowSubmissionForm(false)}
                  className="bg-gray-200 text-gray-800 px-6 py-2 rounded-lg hover:bg-gray-300 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Submit Request
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Requests List */}
        <div className="bg-white rounded-xl shadow-lg">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-xl font-bold text-gray-800">Your Submitted Requests</h2>
          </div>
          
          {requests.length === 0 ? (
            <div className="p-8 text-center">
              <div className="text-gray-400 text-6xl mb-4">📝</div>
              <h3 className="text-lg font-medium text-gray-800 mb-2">No requests yet</h3>
              <p className="text-gray-600 mb-4">Submit your first request to get started!</p>
              <button
                onClick={() => setShowSubmissionForm(true)}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
              >
                Submit First Request
              </button>
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {requests.map((request) => (
                <div key={request.id} className="p-6 hover:bg-gray-50 transition-colors">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h3 className="text-lg font-medium text-gray-800">{request.title}</h3>
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                          request.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                          request.status === 'in_progress' ? 'bg-blue-100 text-blue-800' :
                          request.status === 'resolved' ? 'bg-green-100 text-green-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {request.status.replace('_', ' ').toUpperCase()}
                        </span>
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                          request.priority === 'low' ? 'bg-gray-100 text-gray-800' :
                          request.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                          request.priority === 'high' ? 'bg-orange-100 text-orange-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {request.priority.toUpperCase()}
                        </span>
                      </div>
                      <p className="text-gray-600 mb-3">{request.description}</p>
                      <div className="flex items-center space-x-4 text-sm text-gray-500">
                        <span>Type: {request.request_type.replace('_', ' ')}</span>
                        <span>•</span>
                        <span>Submitted: {new Date(request.created_at).toLocaleDateString()}</span>
                        {request.category && (
                          <>
                            <span>•</span>
                            <span>Category: {request.category}</span>
                          </>
                        )}
                      </div>
                      {request.admin_response && (
                        <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                          <div className="text-sm font-medium text-blue-800 mb-1">Admin Response:</div>
                          <div className="text-blue-700">{request.admin_response}</div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

function App() {
  const [currentView, setCurrentView] = useState('home'); // 'home', 'browse', 'profile', 'requests', 'garage', 'community', or 'achievements'
  const [motorcycles, setMotorcycles] = useState([]);
  const [categories, setCategories] = useState([]);
  const [availableFeatures, setAvailableFeatures] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedMotorcycle, setSelectedMotorcycle] = useState(null);
  const [filters, setFilters] = useState({});
  const [filterOptions, setFilterOptions] = useState({});
  const [sortBy, setSortBy] = useState('default');
  const [sortOrder, setSortOrder] = useState('desc');
  const [showFilters, setShowFilters] = useState(false);
  const [databaseStats, setDatabaseStats] = useState({ totalMotorcycles: 0, totalManufacturers: 0 });
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [pagination, setPagination] = useState({});

  // Analytics helper functions
  const logSearchAnalytics = async (searchTerm, searchType = 'general', filtersApplied = {}, resultsCount = 0, clickedResults = []) => {
    try {
      await axios.post(`${API}/analytics/search`, {
        search_term: searchTerm,
        search_type: searchType,
        filters_applied: filtersApplied,
        results_count: resultsCount,
        clicked_results: clickedResults
      });
    } catch (error) {
      console.log('Analytics logging failed:', error); // Non-blocking
    }
  };

  const logEngagement = async (pageView, timeSpent = null, actions = [], referrer = null) => {
    try {
      await axios.post(`${API}/analytics/engagement`, {
        page_view: pageView,
        time_spent: timeSpent,
        actions: actions,
        referrer: referrer
      });
    } catch (error) {
      console.log('Engagement logging failed:', error); // Non-blocking
    }
  };

  // Track page views and engagement
  useEffect(() => {
    // Log page view
    logEngagement(currentView, null, [], document.referrer);
    
    // Track time spent on page
    const startTime = Date.now();
    
    return () => {
      const timeSpent = Math.floor((Date.now() - startTime) / 1000);
      if (timeSpent > 1) { // Only log if spent more than 1 second
        logEngagement(currentView, timeSpent);
      }
    };
  }, [currentView]);

  // Enhanced fetchMotorcycles with analytics tracking
  const fetchMotorcycles = async (page = 1) => {
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
      params.append('page', page.toString());
      params.append('limit', '25'); // 25 motorcycles per page
      
      const response = await axios.get(`${API}/motorcycles?${params.toString()}`);
      setMotorcycles(response.data.motorcycles);
      setPagination(response.data.pagination);
      setCurrentPage(response.data.pagination.page);
      setTotalPages(response.data.pagination.total_pages);
      
      // Log search analytics
      const searchTerm = filters.search || '';
      const searchType = filters.manufacturer ? 'manufacturer' : 
                        filters.category ? 'category' : 
                        filters.price_range ? 'price_range' : 'general';
      
      if (searchTerm || Object.keys(filters).length > 0) {
        logSearchAnalytics(
          searchTerm,
          searchType,
          filters,
          response.data.motorcycles.length
        );
      }
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

  const fetchAvailableFeatures = async () => {
    try {
      const response = await axios.get(`${API}/motorcycles/filters/features`);
      setAvailableFeatures(response.data.features);
    } catch (error) {
      console.error('Error fetching features:', error);
    }
  };

  const fetchDatabaseStats = async () => {
    try {
      const response = await axios.get(`${API}/stats`);
      setDatabaseStats({
        totalMotorcycles: response.data.total_motorcycles,
        totalManufacturers: response.data.manufacturers.length // Get length of manufacturers array
      });
    } catch (error) {
      console.error('Error fetching database stats:', error);
      // Set fallback stats
      setDatabaseStats({
        totalMotorcycles: 0,
        totalManufacturers: 0
      });
      // Fallback to calculating from categories if stats API fails
      const totalFromCategories = categories.reduce((sum, cat) => sum + cat.count, 0);
      const totalManufacturersFromFilter = filterOptions.manufacturers?.length || 0;
      setDatabaseStats({
        totalMotorcycles: totalFromCategories,
        totalManufacturers: totalManufacturersFromFilter
      });
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

  const handlePageChange = (newPage) => {
    setCurrentPage(newPage);
    fetchMotorcycles(newPage);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleViewAllCategory = (categoryName) => {
    setCurrentView('browse');
    setFilters({ category: categoryName });
    setCurrentPage(1); // Reset to first page when changing filters
    window.history.pushState({}, '', '/browse');
  };

  const handleCategoryButtonClick = (categoryName) => {
    setCurrentView('browse');
    setFilters({ category: categoryName });
    setCurrentPage(1); // Reset to first page when changing category
    window.history.pushState({}, '', '/browse');
  };

  useEffect(() => {
    fetchFilterOptions();
    fetchAvailableFeatures();
    seedDatabase(); // Seed on first load
  }, []);

  useEffect(() => {
    fetchDatabaseStats();
  }, [categories, filterOptions]);

  useEffect(() => {
    // Refetch stats when view changes to home to ensure fresh data
    if (currentView === 'home') {
      fetchDatabaseStats();
    }
  }, [currentView]);

  useEffect(() => {
    if (currentView === 'browse') {
      setCurrentPage(1); // Reset to first page when filters change
      fetchMotorcycles(1);
    }
  }, [filters, sortBy, sortOrder, currentView]);

  // Handle route changes
  useEffect(() => {
    const path = window.location.pathname;
    if (path === '/profile') {
      setCurrentView('profile');
    } else if (path === '/browse') {
      setCurrentView('browse');
    } else if (path === '/requests') {
      setCurrentView('requests');
    } else if (path === '/garage') {
      setCurrentView('garage');
    } else if (path === '/community') {
      setCurrentView('community');
    } else if (path === '/achievements') {
      setCurrentView('achievements');
    } else {
      setCurrentView('home');
    }
  }, []);

  // Calculate statistics from database stats API instead of categories sum
  const totalMotorcycles = databaseStats.totalMotorcycles;
  const totalManufacturers = databaseStats.totalManufacturers;

  return (
    <AuthProvider>
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <div className="flex items-center">
                <button 
                  onClick={() => {setCurrentView('home'); window.history.pushState({}, '', '/');}}
                  className="text-2xl font-bold text-gray-900 hover:text-blue-600 transition-colors"
                >
                  Bike-Dream
                </button>
                <span className="ml-2 text-sm text-gray-500">Motorcycle Database</span>
              </div>
              <div className="flex items-center space-x-4">
                <button
                  onClick={() => {setCurrentView('home'); window.history.pushState({}, '', '/');}}
                  className={`px-4 py-2 rounded-lg transition-colors ${
                    currentView === 'home' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:text-blue-600'
                  }`}
                >
                  Home
                </button>
                <button
                  onClick={() => {setCurrentView('browse'); window.history.pushState({}, '', '/browse');}}
                  className={`px-4 py-2 rounded-lg transition-colors ${
                    currentView === 'browse' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:text-blue-600'
                  }`}
                >
                  Browse All
                </button>
                <button
                  onClick={() => {setCurrentView('profile'); window.history.pushState({}, '', '/profile');}}
                  className={`px-4 py-2 rounded-lg transition-colors ${
                    currentView === 'profile' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:text-blue-600'
                  }`}
                >
                  Profile
                </button>
                <button
                  onClick={() => {setCurrentView('requests'); window.history.pushState({}, '', '/requests');}}
                  className={`px-4 py-2 rounded-lg transition-colors ${
                    currentView === 'requests' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:text-blue-600'
                  }`}
                >
                  Requests
                </button>
                <button
                  onClick={() => {setCurrentView('garage'); window.history.pushState({}, '', '/garage');}}
                  className={`px-4 py-2 rounded-lg transition-colors ${
                    currentView === 'garage' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:text-blue-600'
                  }`}
                >
                  My Garage
                </button>
                <button
                  onClick={() => {setCurrentView('community'); window.history.pushState({}, '', '/community');}}
                  className={`px-4 py-2 rounded-lg transition-colors ${
                    currentView === 'community' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:text-blue-600'
                  }`}
                >
                  Community
                </button>
                <button
                  onClick={() => {setCurrentView('achievements'); window.history.pushState({}, '', '/achievements');}}
                  className={`px-4 py-2 rounded-lg transition-colors ${
                    currentView === 'achievements' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:text-blue-600'
                  }`}
                >
                  Achievements
                </button>
                <button
                  onClick={() => {setCurrentView('analytics'); window.history.pushState({}, '', '/analytics');}}
                  className={`px-4 py-2 rounded-lg transition-colors ${
                    currentView === 'analytics' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:text-blue-600'
                  }`}
                >
                  Analytics
                </button>
                <AuthButton />
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
                      <option value="default-desc">Default (New → Old, Low → High Price)</option>
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

        {currentView === 'profile' ? (
          <ProfilePage />
        ) : currentView === 'requests' ? (
          <UserRequestsPage />
        ) : currentView === 'garage' ? (
          <VirtualGaragePage />
        ) : currentView === 'community' ? (
          <CommunityPage />
        ) : currentView === 'achievements' ? (
          <AchievementsPage />
        ) : currentView === 'home' ? (
          // Home Page
          <>
            {/* Hero Carousel Section */}
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
              <HeroCarousel onViewChange={setCurrentView} />
            </div>

            {/* Stats Section */}
            <div className="bg-gray-50 py-16">
              <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-8 text-center">
                  <div className="bg-white p-8 rounded-xl shadow-lg">
                    <div className="text-5xl font-bold text-blue-600 mb-3">
                      {totalMotorcycles.toLocaleString()}+
                    </div>
                    <div className="text-gray-600 text-lg">Motorcycles Listed</div>
                  </div>
                  <div className="bg-white p-8 rounded-xl shadow-lg">
                    <div className="text-5xl font-bold text-green-600 mb-3">
                      {totalManufacturers}+
                    </div>
                    <div className="text-gray-600 text-lg">Manufacturers</div>
                  </div>
                  <div className="bg-white p-8 rounded-xl shadow-lg">
                    <div className="text-5xl font-bold text-purple-600 mb-3">125+</div>
                    <div className="text-gray-600 text-lg">Years of History</div>
                  </div>
                  <div className="bg-white p-8 rounded-xl shadow-lg">
                    <div className="text-5xl font-bold text-red-600 mb-3">67+</div>
                    <div className="text-gray-600 text-lg">Countries Supported</div>
                  </div>
                </div>
                
                {/* Quick Category Buttons */}
                <div className="mt-16 text-center">
                  <h3 className="text-2xl font-bold text-gray-800 mb-6">Explore by Category</h3>
                  <div className="flex flex-wrap justify-center gap-3">
                    {['Sport', 'Cruiser', 'Touring', 'Adventure', 'Naked', 'Vintage', 'Scooter', 'Standard', 'Enduro', 'Motocross'].map((category) => (
                      <button
                        key={category}
                        onClick={() => handleCategoryButtonClick(category)}
                        className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium shadow-lg hover:shadow-xl transform hover:scale-105"
                      >
                        {category}
                      </button>
                    ))}
                  </div>
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
                      onViewAllClick={handleViewAllCategory}
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
                  availableFeatures={availableFeatures}
                  isOpen={showFilters}
                  onToggle={() => setShowFilters(!showFilters)}
                />
              </div>

              {/* Motorcycle Grid */}
              <div className="flex-1">
                <div className="mb-6">
                  <h1 className="text-3xl font-bold text-gray-800">
                    All Motorcycles ({pagination.total_count || 0})
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
                      onClick={() => {setFilters({}); setCurrentPage(1);}}
                      className="mt-4 bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      Clear Filters
                    </button>
                  </div>
                ) : (
                  <>
                    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                      {motorcycles.map((motorcycle) => (
                        <MotorcycleCard
                          key={motorcycle.id}
                          motorcycle={motorcycle}
                          onClick={setSelectedMotorcycle}
                        />
                      ))}
                    </div>
                    
                    <PaginationControls
                      currentPage={currentPage}
                      totalPages={totalPages}
                      onPageChange={handlePageChange}
                      totalCount={pagination.total_count || 0}
                      limit={pagination.limit || 25}
                    />
                  </>
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
    </AuthProvider>
  );
}

export default App;