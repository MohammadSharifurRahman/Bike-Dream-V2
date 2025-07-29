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
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    const sessionId = localStorage.getItem('session_id');
    if (sessionId) {
      try {
        const response = await axios.get(`${API}/auth/me`, {
          headers: { 'X-Session-ID': sessionId }
        });
        setUser(response.data);
      } catch (error) {
        localStorage.removeItem('session_id');
      }
    }
    setLoading(false);
  };

  const login = () => {
    const previewUrl = window.location.origin;
    window.location.href = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(previewUrl + '/profile')}`;
  };

  const logout = () => {
    localStorage.removeItem('session_id');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

const useAuth = () => useContext(AuthContext);

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
const VendorPricing = ({ motorcycle, region = "US" }) => {
  const [vendorPrices, setVendorPrices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedRegion, setSelectedRegion] = useState(region);
  const [supportedRegions, setSupportedRegions] = useState([]);

  useEffect(() => {
    fetchSupportedRegions();
  }, []);

  useEffect(() => {
    fetchVendorPrices();
  }, [motorcycle.id, selectedRegion]);

  const fetchSupportedRegions = async () => {
    try {
      const response = await axios.get(`${API}/pricing/regions`);
      setSupportedRegions(response.data.regions);
    } catch (error) {
      console.error('Error fetching regions:', error);
    }
  };

  const fetchVendorPrices = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/motorcycles/${motorcycle.id}/pricing?region=${selectedRegion}`);
      setVendorPrices(response.data.vendor_prices);
    } catch (error) {
      console.error('Error fetching vendor prices:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatPrice = (price, currency) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency
    }).format(price);
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg mb-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-bold text-gray-800">Vendor Pricing</h3>
        <select
          value={selectedRegion}
          onChange={(e) => setSelectedRegion(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          {supportedRegions.map(region => (
            <option key={region.code} value={region.code}>
              {region.name} ({region.currency})
            </option>
          ))}
        </select>
      </div>

      {loading ? (
        <div className="flex justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      ) : (
        <div className="space-y-4">
          {vendorPrices.map((vendor, index) => (
            <div key={index} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-3">
                  <h4 className="font-semibold text-lg">{vendor.vendor_name}</h4>
                  <div className="flex items-center space-x-1">
                    <StarRating rating={Math.round(vendor.rating)} readOnly />
                    <span className="text-sm text-gray-500">({vendor.reviews_count})</span>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-green-600">
                    {formatPrice(vendor.price, vendor.currency)}
                  </div>
                  {index === 0 && (
                    <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">
                      Best Price
                    </span>
                  )}
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4 text-sm text-gray-600 mb-3">
                <div>
                  <span className="font-medium">Availability:</span> {vendor.availability}
                </div>
                <div>
                  <span className="font-medium">Shipping:</span> {vendor.shipping}
                </div>
                <div>
                  <span className="font-medium">Delivery:</span> {vendor.estimated_delivery}
                </div>
                {vendor.special_offer && (
                  <div className="col-span-2">
                    <span className="font-medium text-blue-600">Special Offer:</span> {vendor.special_offer}
                  </div>
                )}
              </div>
              
              <div className="flex space-x-3">
                <a
                  href={vendor.website_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors text-sm"
                >
                  Visit Store
                </a>
                {vendor.phone && (
                  <a
                    href={`tel:${vendor.phone}`}
                    className="bg-gray-200 text-gray-800 px-4 py-2 rounded-lg hover:bg-gray-300 transition-colors text-sm"
                  >
                    Call {vendor.phone}
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// Rating and Review Component
const RatingSection = ({ motorcycle, onRatingSubmit }) => {
  const { user } = useAuth();
  const [userRating, setUserRating] = useState(0);
  const [reviewText, setReviewText] = useState('');
  const [ratings, setRatings] = useState([]);
  const [showRatingForm, setShowRatingForm] = useState(false);

  useEffect(() => {
    fetchRatings();
  }, [motorcycle.id]);

  const fetchRatings = async () => {
    try {
      const response = await axios.get(`${API}/motorcycles/${motorcycle.id}/ratings`);
      setRatings(response.data);
    } catch (error) {
      console.error('Error fetching ratings:', error);
    }
  };

  const handleSubmitRating = async () => {
    if (!user) return;

    try {
      const sessionId = localStorage.getItem('session_id');
      await axios.post(`${API}/motorcycles/${motorcycle.id}/rate`, {
        motorcycle_id: motorcycle.id,
        rating: userRating,
        review_text: reviewText
      }, {
        headers: { 'X-Session-ID': sessionId }
      });

      setUserRating(0);
      setReviewText('');
      setShowRatingForm(false);
      fetchRatings();
      if (onRatingSubmit) onRatingSubmit();
    } catch (error) {
      console.error('Error submitting rating:', error);
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg mb-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-bold text-gray-800">Ratings & Reviews</h3>
        {motorcycle.average_rating > 0 && (
          <div className="flex items-center space-x-2">
            <StarRating rating={Math.round(motorcycle.average_rating)} readOnly />
            <span className="text-lg font-semibold">{motorcycle.average_rating}</span>
            <span className="text-gray-500">({motorcycle.total_ratings} reviews)</span>
          </div>
        )}
      </div>

      {user && (
        <div className="mb-6">
          {!showRatingForm ? (
            <button
              onClick={() => setShowRatingForm(true)}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Write a Review
            </button>
          ) : (
            <div className="border border-gray-200 p-4 rounded-lg">
              <h4 className="font-semibold mb-3">Rate this motorcycle:</h4>
              <div className="mb-4">
                <StarRating rating={userRating} onRatingChange={setUserRating} />
              </div>
              <textarea
                value={reviewText}
                onChange={(e) => setReviewText(e.target.value)}
                placeholder="Share your thoughts about this motorcycle..."
                className="w-full p-3 border border-gray-300 rounded-lg resize-none h-32 mb-4"
              />
              <div className="flex space-x-3">
                <button
                  onClick={handleSubmitRating}
                  disabled={userRating === 0}
                  className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:bg-gray-400 transition-colors"
                >
                  Submit Review
                </button>
                <button
                  onClick={() => {setShowRatingForm(false); setUserRating(0); setReviewText('');}}
                  className="bg-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-400 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {ratings.length > 0 && (
        <div className="space-y-4">
          <h4 className="font-semibold text-gray-800">User Reviews:</h4>
          {ratings.map((rating) => (
            <div key={rating.id} className="border-l-4 border-blue-500 pl-4 py-2">
              <div className="flex items-center space-x-3 mb-2">
                <img
                  src={rating.user_picture || '/default-avatar.png'}
                  alt={rating.user_name}
                  className="w-8 h-8 rounded-full"
                />
                <span className="font-medium">{rating.user_name}</span>
                <StarRating rating={rating.rating} readOnly />
                <span className="text-sm text-gray-500">
                  {new Date(rating.created_at).toLocaleDateString()}
                </span>
              </div>
              {rating.review_text && (
                <p className="text-gray-700 pl-11">{rating.review_text}</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// Comments Section Component
const CommentsSection = ({ motorcycle }) => {
  const { user } = useAuth();
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');
  const [replyingTo, setReplyingTo] = useState(null);
  const [replyText, setReplyText] = useState('');

  useEffect(() => {
    fetchComments();
  }, [motorcycle.id]);

  const fetchComments = async () => {
    try {
      const response = await axios.get(`${API}/motorcycles/${motorcycle.id}/comments`);
      setComments(response.data);
    } catch (error) {
      console.error('Error fetching comments:', error);
    }
  };

  const handleSubmitComment = async () => {
    if (!user || !newComment.trim()) return;

    try {
      const sessionId = localStorage.getItem('session_id');
      await axios.post(`${API}/motorcycles/${motorcycle.id}/comment`, {
        motorcycle_id: motorcycle.id,
        comment_text: newComment
      }, {
        headers: { 'X-Session-ID': sessionId }
      });

      setNewComment('');
      fetchComments();
    } catch (error) {
      console.error('Error submitting comment:', error);
    }
  };

  const handleSubmitReply = async (parentId) => {
    if (!user || !replyText.trim()) return;

    try {
      const sessionId = localStorage.getItem('session_id');
      await axios.post(`${API}/motorcycles/${motorcycle.id}/comment`, {
        motorcycle_id: motorcycle.id,
        comment_text: replyText,
        parent_comment_id: parentId
      }, {
        headers: { 'X-Session-ID': sessionId }
      });

      setReplyText('');
      setReplyingTo(null);
      fetchComments();
    } catch (error) {
      console.error('Error submitting reply:', error);
    }
  };

  const handleLikeComment = async (commentId) => {
    if (!user) return;

    try {
      const sessionId = localStorage.getItem('session_id');
      await axios.post(`${API}/comments/${commentId}/like`, {}, {
        headers: { 'X-Session-ID': sessionId }
      });
      fetchComments();
    } catch (error) {
      console.error('Error liking comment:', error);
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg">
      <h3 className="text-xl font-bold text-gray-800 mb-4">
        Discussion ({motorcycle.total_comments || comments.length})
      </h3>

      {user && (
        <div className="mb-6">
          <textarea
            value={newComment}
            onChange={(e) => setNewComment(e.target.value)}
            placeholder="Share your thoughts about this motorcycle..."
            className="w-full p-3 border border-gray-300 rounded-lg resize-none h-24 mb-3"
          />
          <button
            onClick={handleSubmitComment}
            disabled={!newComment.trim()}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
          >
            Post Comment
          </button>
        </div>
      )}

      {!user && (
        <div className="bg-gray-50 p-4 rounded-lg mb-6 text-center">
          <p className="text-gray-600 mb-2">Join the discussion!</p>
          <AuthButton />
        </div>
      )}

      <div className="space-y-4">
        {comments.map((comment) => (
          <div key={comment.id} className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-start space-x-3">
              <img
                src={comment.user_picture || '/default-avatar.png'}
                alt={comment.user_name}
                className="w-10 h-10 rounded-full"
              />
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-2">
                  <span className="font-medium text-gray-800">{comment.user_name}</span>
                  <span className="text-sm text-gray-500">
                    {new Date(comment.created_at).toLocaleDateString()}
                  </span>
                </div>
                <p className="text-gray-700 mb-3">{comment.comment_text}</p>
                <div className="flex items-center space-x-4 text-sm">
                  <button
                    onClick={() => handleLikeComment(comment.id)}
                    className="flex items-center space-x-1 text-gray-500 hover:text-blue-600 transition-colors"
                  >
                    <span>👍</span>
                    <span>{comment.likes}</span>
                  </button>
                  {user && (
                    <button
                      onClick={() => setReplyingTo(comment.id)}
                      className="text-gray-500 hover:text-blue-600 transition-colors"
                    >
                      Reply
                    </button>
                  )}
                </div>

                {replyingTo === comment.id && (
                  <div className="mt-3 pl-4 border-l-2 border-gray-200">
                    <textarea
                      value={replyText}
                      onChange={(e) => setReplyText(e.target.value)}
                      placeholder="Write your reply..."
                      className="w-full p-2 border border-gray-300 rounded-lg resize-none h-20 mb-2"
                    />
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleSubmitReply(comment.id)}
                        disabled={!replyText.trim()}
                        className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700 disabled:bg-gray-400"
                      >
                        Reply
                      </button>
                      <button
                        onClick={() => {setReplyingTo(null); setReplyText('');}}
                        className="bg-gray-300 text-gray-700 px-3 py-1 rounded text-sm hover:bg-gray-400"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                )}

                {comment.replies && comment.replies.length > 0 && (
                  <div className="mt-4 pl-4 border-l-2 border-gray-200 space-y-3">
                    {comment.replies.map((reply) => (
                      <div key={reply.id} className="flex items-start space-x-3">
                        <img
                          src={reply.user_picture || '/default-avatar.png'}
                          alt={reply.user_name}
                          className="w-8 h-8 rounded-full"
                        />
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-1">
                            <span className="font-medium text-gray-800">{reply.user_name}</span>
                            <span className="text-xs text-gray-500">
                              {new Date(reply.created_at).toLocaleDateString()}
                            </span>
                          </div>
                          <p className="text-gray-700 text-sm">{reply.comment_text}</p>
                          <button
                            onClick={() => handleLikeComment(reply.id)}
                            className="flex items-center space-x-1 text-xs text-gray-500 hover:text-blue-600 mt-1"
                          >
                            <span>👍</span>
                            <span>{reply.likes}</span>
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Authentication Components
const AuthButton = () => {
  const { user, login, logout } = useAuth();

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
    <button
      onClick={login}
      className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
    >
      Login / Sign Up
    </button>
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

const MotorcycleCard = ({ motorcycle, onClick, showFavoriteButton = true }) => {
  const { user } = useAuth();
  const [isFavorite, setIsFavorite] = useState(false);

  const handleFavoriteToggle = async (e) => {
    e.stopPropagation();
    if (!user) return;

    try {
      const sessionId = localStorage.getItem('session_id');
      if (isFavorite) {
        await axios.delete(`${API}/motorcycles/${motorcycle.id}/favorite`, {
          headers: { 'X-Session-ID': sessionId }
        });
        setIsFavorite(false);
      } else {
        await axios.post(`${API}/motorcycles/${motorcycle.id}/favorite`, {}, {
          headers: { 'X-Session-ID': sessionId }
        });
        setIsFavorite(true);
      }
    } catch (error) {
      console.error('Error toggling favorite:', error);
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
        {showFavoriteButton && user && (
          <button
            onClick={handleFavoriteToggle}
            className={`absolute top-4 left-1/2 transform -translate-x-1/2 w-10 h-10 rounded-full flex items-center justify-center transition-colors ${
              isFavorite ? 'bg-red-500 text-white' : 'bg-white text-gray-400 hover:text-red-500'
            }`}
          >
            ❤️
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

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-xl max-w-6xl w-full max-h-screen overflow-y-auto">
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
            <CommentsSection motorcycle={motorcycle} />
          )}
        </div>
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

function App() {
  const [currentView, setCurrentView] = useState('home'); // 'home', 'browse', or 'profile'
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
      params.append('limit', '5000'); // Show all motorcycles
      
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
        totalManufacturers: response.data.manufacturers
      });
    } catch (error) {
      console.error('Error fetching database stats:', error);
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

  const handleViewAllCategory = (categoryName) => {
    setCurrentView('browse');
    setFilters({ category: categoryName });
    window.history.pushState({}, '', '/browse');
  };

  const handleCategoryButtonClick = (categoryName) => {
    setCurrentView('browse');
    setFilters({ category: categoryName });
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
    if (currentView === 'browse') {
      fetchMotorcycles();
    }
  }, [filters, sortBy, sortOrder, currentView]);

  // Handle route changes
  useEffect(() => {
    const path = window.location.pathname;
    if (path === '/profile') {
      setCurrentView('profile');
    } else if (path === '/browse') {
      setCurrentView('browse');
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
        ) : currentView === 'home' ? (
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
                  
                  <div className="flex flex-col items-center space-y-6">
                    <button
                      onClick={() => {setCurrentView('browse'); window.history.pushState({}, '', '/browse');}}
                      className="bg-white text-blue-900 px-8 py-4 rounded-lg text-lg font-semibold hover:bg-blue-50 transition-colors"
                    >
                      Explore All Motorcycles
                    </button>
                    
                    {/* Quick Category Buttons */}
                    <div className="mt-8">
                      <p className="text-blue-100 mb-4 text-lg">Or explore by category:</p>
                      <div className="flex flex-wrap justify-center gap-3">
                        {['Sport', 'Cruiser', 'Touring', 'Adventure', 'Naked', 'Vintage', 'Scooter', 'Standard', 'Enduro', 'Motocross'].map((category) => (
                          <button
                            key={category}
                            onClick={() => handleCategoryButtonClick(category)}
                            className="bg-blue-700 bg-opacity-50 text-white px-4 py-2 rounded-lg hover:bg-opacity-70 transition-colors text-sm font-medium"
                          >
                            {category}
                          </button>
                        ))}
                      </div>
                    </div>
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
    </AuthProvider>
  );
}

export default App;