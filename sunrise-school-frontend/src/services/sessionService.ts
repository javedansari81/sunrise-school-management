/**
 * Session Management Service
 * Handles token validation, session expiration detection, and session cleanup
 */

interface SessionEventCallbacks {
  onSessionExpired?: () => void;
  onSessionInvalid?: () => void;
  onSessionCleared?: () => void;
}

class SessionService {
  private callbacks: SessionEventCallbacks = {};
  private checkInterval: NodeJS.Timeout | null = null;
  private readonly CHECK_INTERVAL_MS = 60000; // Check every minute

  /**
   * Register callbacks for session events
   */
  setCallbacks(callbacks: SessionEventCallbacks) {
    this.callbacks = { ...this.callbacks, ...callbacks };
  }

  /**
   * Start periodic session validation
   */
  startSessionMonitoring() {
    if (this.checkInterval) {
      clearInterval(this.checkInterval);
    }

    this.checkInterval = setInterval(() => {
      this.validateCurrentSession();
    }, this.CHECK_INTERVAL_MS);
  }

  /**
   * Stop periodic session validation
   */
  stopSessionMonitoring() {
    if (this.checkInterval) {
      clearInterval(this.checkInterval);
      this.checkInterval = null;
    }
  }

  /**
   * Check if a JWT token is expired
   */
  isTokenExpired(token: string): boolean {
    try {
      // Decode JWT token without verification (just to check expiration)
      const payload = JSON.parse(atob(token.split('.')[1]));
      const currentTime = Math.floor(Date.now() / 1000);
      
      return payload.exp < currentTime;
    } catch (error) {
      console.error('Error parsing token:', error);
      return true; // Consider invalid tokens as expired
    }
  }

  /**
   * Get token expiration time
   */
  getTokenExpiration(token: string): Date | null {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return new Date(payload.exp * 1000);
    } catch (error) {
      console.error('Error parsing token expiration:', error);
      return null;
    }
  }

  /**
   * Check if current session is valid
   */
  isSessionValid(): boolean {
    const token = localStorage.getItem('authToken');
    
    if (!token) {
      return false;
    }

    return !this.isTokenExpired(token);
  }

  /**
   * Validate current session and trigger appropriate callbacks
   */
  validateCurrentSession(): boolean {
    const token = localStorage.getItem('authToken');
    
    if (!token) {
      console.log('SessionService: No token found');
      return false;
    }

    if (this.isTokenExpired(token)) {
      console.log('SessionService: Token expired, triggering session expired callback');
      this.handleSessionExpired();
      return false;
    }

    return true;
  }

  /**
   * Handle session expiration
   */
  private handleSessionExpired() {
    this.clearSession();
    if (this.callbacks.onSessionExpired) {
      this.callbacks.onSessionExpired();
    }
  }

  /**
   * Handle invalid session
   */
  handleSessionInvalid() {
    console.log('SessionService: Invalid session detected');
    this.clearSession();
    if (this.callbacks.onSessionInvalid) {
      this.callbacks.onSessionInvalid();
    }
  }

  /**
   * Clear session data
   */
  clearSession() {
    console.log('SessionService: Clearing session data');
    localStorage.removeItem('authToken');
    localStorage.removeItem('userRole');
    
    if (this.callbacks.onSessionCleared) {
      this.callbacks.onSessionCleared();
    }
  }

  /**
   * Get time until token expiration in minutes
   */
  getTimeUntilExpiration(): number | null {
    const token = localStorage.getItem('authToken');
    
    if (!token) {
      return null;
    }

    const expiration = this.getTokenExpiration(token);
    if (!expiration) {
      return null;
    }

    const now = new Date();
    const diffMs = expiration.getTime() - now.getTime();
    return Math.floor(diffMs / (1000 * 60)); // Convert to minutes
  }

  /**
   * Check if session will expire soon (within specified minutes)
   */
  willExpireSoon(withinMinutes: number = 5): boolean {
    const timeUntilExpiration = this.getTimeUntilExpiration();
    return timeUntilExpiration !== null && timeUntilExpiration <= withinMinutes;
  }
}

// Create singleton instance
export const sessionService = new SessionService();
export default sessionService;
