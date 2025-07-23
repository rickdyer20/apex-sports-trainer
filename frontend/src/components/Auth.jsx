// Basketball Analysis Service - Frontend Authentication Components
// React components for user authentication and subscription management

import React, { useState, useEffect, createContext, useContext } from 'react';
import axios from 'axios';

// Authentication Context
const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Auth Provider Component
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [subscription, setSubscription] = useState(null);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      if (token) {
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        const response = await axios.get('/auth/profile');
        setUser(response.data.user);
        await loadSubscription();
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      localStorage.removeItem('auth_token');
    } finally {
      setLoading(false);
    }
  };

  const loadSubscription = async () => {
    try {
      const response = await axios.get('/payment/subscription/status');
      setSubscription(response.data.subscription);
    } catch (error) {
      console.error('Failed to load subscription:', error);
    }
  };

  const login = async (email, password) => {
    try {
      const response = await axios.post('/auth/email/login', { email, password });
      const { token, user } = response.data;
      
      localStorage.setItem('auth_token', token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      setUser(user);
      await loadSubscription();
      
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Login failed' 
      };
    }
  };

  const register = async (userData) => {
    try {
      const response = await axios.post('/auth/email/register', userData);
      return { success: true, message: response.data.message };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Registration failed' 
      };
    }
  };

  const logout = async () => {
    try {
      await axios.post('/auth/logout');
    } catch (error) {
      console.error('Logout request failed:', error);
    } finally {
      localStorage.removeItem('auth_token');
      delete axios.defaults.headers.common['Authorization'];
      setUser(null);
      setSubscription(null);
    }
  };

  const value = {
    user,
    subscription,
    loading,
    login,
    register,
    logout,
    loadSubscription
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Login Component
export const LoginForm = ({ onSuccess }) => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrors({});

    const result = await login(formData.email, formData.password);
    
    if (result.success) {
      onSuccess?.();
    } else {
      setErrors({ general: result.error });
    }
    setLoading(false);
  };

  const handleOAuthLogin = (provider) => {
    window.location.href = `/auth/${provider}`;
  };

  return (
    <div className="login-form">
      <h2>Sign In to Basketball Analysis</h2>
      
      {/* OAuth Login Options */}
      <div className="oauth-buttons">
        <button 
          onClick={() => handleOAuthLogin('google')}
          className="oauth-btn google-btn"
        >
          <img src="/icons/google.svg" alt="Google" />
          Continue with Google
        </button>
        
        <button 
          onClick={() => handleOAuthLogin('github')}
          className="oauth-btn github-btn"
        >
          <img src="/icons/github.svg" alt="GitHub" />
          Continue with GitHub
        </button>
        
        <button 
          onClick={() => handleOAuthLogin('microsoft')}
          className="oauth-btn microsoft-btn"
        >
          <img src="/icons/microsoft.svg" alt="Microsoft" />
          Continue with Microsoft
        </button>
      </div>

      <div className="divider">
        <span>or continue with email</span>
      </div>

      {/* Email/Password Form */}
      <form onSubmit={handleSubmit}>
        {errors.general && (
          <div className="error-message">{errors.general}</div>
        )}
        
        <div className="form-group">
          <label htmlFor="email">Email</label>
          <input
            type="email"
            id="email"
            value={formData.email}
            onChange={(e) => setFormData({...formData, email: e.target.value})}
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="password">Password</label>
          <input
            type="password"
            id="password"
            value={formData.password}
            onChange={(e) => setFormData({...formData, password: e.target.value})}
            required
          />
        </div>
        
        <button type="submit" disabled={loading} className="submit-btn">
          {loading ? 'Signing In...' : 'Sign In'}
        </button>
      </form>
      
      <div className="form-links">
        <a href="/auth/forgot-password">Forgot Password?</a>
        <span>Don't have an account? <a href="/register">Sign Up</a></span>
      </div>
    </div>
  );
};

// Registration Component
export const RegisterForm = ({ onSuccess }) => {
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrors({});

    // Validate passwords match
    if (formData.password !== formData.confirmPassword) {
      setErrors({ confirmPassword: 'Passwords do not match' });
      setLoading(false);
      return;
    }

    const result = await register({
      first_name: formData.firstName,
      last_name: formData.lastName,
      email: formData.email,
      password: formData.password
    });

    if (result.success) {
      onSuccess?.(result.message);
    } else {
      setErrors({ general: result.error });
    }
    setLoading(false);
  };

  return (
    <div className="register-form">
      <h2>Create Your Account</h2>
      
      <form onSubmit={handleSubmit}>
        {errors.general && (
          <div className="error-message">{errors.general}</div>
        )}
        
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="firstName">First Name</label>
            <input
              type="text"
              id="firstName"
              value={formData.firstName}
              onChange={(e) => setFormData({...formData, firstName: e.target.value})}
              required
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="lastName">Last Name</label>
            <input
              type="text"
              id="lastName"
              value={formData.lastName}
              onChange={(e) => setFormData({...formData, lastName: e.target.value})}
              required
            />
          </div>
        </div>
        
        <div className="form-group">
          <label htmlFor="email">Email</label>
          <input
            type="email"
            id="email"
            value={formData.email}
            onChange={(e) => setFormData({...formData, email: e.target.value})}
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="password">Password</label>
          <input
            type="password"
            id="password"
            value={formData.password}
            onChange={(e) => setFormData({...formData, password: e.target.value})}
            required
            minLength="8"
          />
          <small>Password must be at least 8 characters long</small>
        </div>
        
        <div className="form-group">
          <label htmlFor="confirmPassword">Confirm Password</label>
          <input
            type="password"
            id="confirmPassword"
            value={formData.confirmPassword}
            onChange={(e) => setFormData({...formData, confirmPassword: e.target.value})}
            required
          />
          {errors.confirmPassword && (
            <div className="field-error">{errors.confirmPassword}</div>
          )}
        </div>
        
        <button type="submit" disabled={loading} className="submit-btn">
          {loading ? 'Creating Account...' : 'Create Account'}
        </button>
      </form>
      
      <div className="form-links">
        <span>Already have an account? <a href="/login">Sign In</a></span>
      </div>
    </div>
  );
};

// Subscription Plans Component
export const SubscriptionPlans = ({ onPlanSelect }) => {
  const [plans, setPlans] = useState([]);
  const [billingCycle, setBillingCycle] = useState('monthly');
  const [loading, setLoading] = useState(true);
  const { subscription } = useAuth();

  useEffect(() => {
    loadPlans();
  }, []);

  const loadPlans = async () => {
    try {
      const response = await axios.get('/payment/plans');
      setPlans(response.data.plans);
    } catch (error) {
      console.error('Failed to load plans:', error);
    } finally {
      setLoading(false);
    }
  };

  const selectPlan = async (planId) => {
    try {
      const response = await axios.post('/payment/create-checkout-session', {
        tier_id: planId,
        billing_cycle: billingCycle
      });
      
      // Redirect to Stripe checkout
      window.location.href = response.data.checkout_url;
    } catch (error) {
      console.error('Failed to create checkout session:', error);
      alert('Failed to start checkout process. Please try again.');
    }
  };

  if (loading) {
    return <div className="loading">Loading subscription plans...</div>;
  }

  return (
    <div className="subscription-plans">
      <h2>Choose Your Plan</h2>
      
      {/* Billing Cycle Toggle */}
      <div className="billing-toggle">
        <button 
          className={billingCycle === 'monthly' ? 'active' : ''}
          onClick={() => setBillingCycle('monthly')}
        >
          Monthly
        </button>
        <button 
          className={billingCycle === 'yearly' ? 'active' : ''}
          onClick={() => setBillingCycle('yearly')}
        >
          Yearly
          <span className="savings-badge">Save 17%</span>
        </button>
      </div>

      {/* Plans Grid */}
      <div className="plans-grid">
        {/* Free Plan */}
        <div className="plan-card free-plan">
          <h3>Free</h3>
          <div className="price">
            <span className="amount">$0</span>
            <span className="period">/month</span>
          </div>
          <ul className="features">
            <li>Basic analysis</li>
            <li>1 video per day</li>
            <li>Community support</li>
          </ul>
          <button 
            className="plan-btn"
            disabled={subscription?.tier === 'free'}
          >
            {subscription?.tier === 'free' ? 'Current Plan' : 'Get Started'}
          </button>
        </div>

        {/* Paid Plans */}
        {plans.map((plan) => {
          const price = billingCycle === 'yearly' ? plan.price_yearly : plan.price_monthly;
          const isCurrentPlan = subscription?.tier === plan.id;
          
          return (
            <div key={plan.id} className={`plan-card ${plan.id === 'pro' ? 'popular' : ''}`}>
              {plan.id === 'pro' && <div className="popular-badge">Most Popular</div>}
              
              <h3>{plan.name}</h3>
              <div className="price">
                <span className="amount">${(price / 100).toFixed(2)}</span>
                <span className="period">/{billingCycle === 'yearly' ? 'year' : 'month'}</span>
              </div>
              
              {billingCycle === 'yearly' && plan.savings_yearly > 0 && (
                <div className="savings">Save ${plan.savings_yearly}/year</div>
              )}
              
              <ul className="features">
                {plan.features.map((feature, index) => (
                  <li key={index}>{feature}</li>
                ))}
              </ul>
              
              <button 
                className="plan-btn"
                onClick={() => selectPlan(plan.id)}
                disabled={isCurrentPlan}
              >
                {isCurrentPlan ? 'Current Plan' : `Choose ${plan.name}`}
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
};

// Usage Dashboard Component
export const UsageDashboard = () => {
  const [usage, setUsage] = useState(null);
  const [loading, setLoading] = useState(true);
  const { subscription } = useAuth();

  useEffect(() => {
    loadUsage();
  }, []);

  const loadUsage = async () => {
    try {
      const response = await axios.get('/payment/usage');
      setUsage(response.data);
    } catch (error) {
      console.error('Failed to load usage:', error);
    } finally {
      setLoading(false);
    }
  };

  const openCustomerPortal = async () => {
    try {
      const response = await axios.post('/payment/portal');
      window.open(response.data.portal_url, '_blank');
    } catch (error) {
      console.error('Failed to open customer portal:', error);
      alert('Failed to open billing portal. Please try again.');
    }
  };

  if (loading) {
    return <div className="loading">Loading usage data...</div>;
  }

  return (
    <div className="usage-dashboard">
      <h2>Subscription & Usage</h2>
      
      {/* Current Plan */}
      <div className="current-plan">
        <h3>Current Plan: {subscription?.tier || 'Free'}</h3>
        {subscription?.status && (
          <p>Status: <span className={`status ${subscription.status}`}>{subscription.status}</span></p>
        )}
        
        {subscription?.tier !== 'free' && (
          <button onClick={openCustomerPortal} className="manage-btn">
            Manage Billing
          </button>
        )}
      </div>

      {/* Usage Statistics */}
      {usage && (
        <div className="usage-stats">
          <h3>This Month's Usage</h3>
          
          <div className="usage-item">
            <div className="usage-label">Videos Analyzed</div>
            <div className="usage-bar">
              <div 
                className="usage-fill"
                style={{ width: `${Math.min(usage.usage_percentage.videos, 100)}%` }}
              />
            </div>
            <div className="usage-text">
              {usage.usage.videos_this_month} / {usage.limits.video_limit === -1 ? '∞' : usage.limits.video_limit}
            </div>
          </div>
          
          <div className="usage-item">
            <div className="usage-label">Analyses Performed</div>
            <div className="usage-bar">
              <div 
                className="usage-fill"
                style={{ width: `${Math.min(usage.usage_percentage.analyses, 100)}%` }}
              />
            </div>
            <div className="usage-text">
              {usage.usage.analyses_this_month} / {usage.limits.analysis_limit === -1 ? '∞' : usage.limits.analysis_limit}
            </div>
          </div>
        </div>
      )}

      {/* Upgrade Prompt */}
      {subscription?.tier === 'free' && (
        <div className="upgrade-prompt">
          <h3>Ready to Level Up?</h3>
          <p>Upgrade to Pro for unlimited analysis and advanced features.</p>
          <a href="/subscribe" className="upgrade-btn">View Plans</a>
        </div>
      )}
    </div>
  );
};

// Protected Route Component
export const ProtectedRoute = ({ children, requireSubscription = false }) => {
  const { user, subscription, loading } = useAuth();

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  if (!user) {
    return <LoginForm onSuccess={() => window.location.reload()} />;
  }

  if (requireSubscription && (!subscription || subscription.tier === 'free')) {
    return (
      <div className="subscription-required">
        <h2>Subscription Required</h2>
        <p>This feature requires a Pro or Enterprise subscription.</p>
        <SubscriptionPlans />
      </div>
    );
  }

  return children;
};
