class CacheService {
  constructor() {
    this.cache = new Map();
    this.expiry = new Map();
    this.defaultTTL = 10 * 60 * 1000; // 10 minutes
  }

  set(key, value, ttl = this.defaultTTL) {
    this.cache.set(key, value);
    this.expiry.set(key, Date.now() + ttl);
  }

  get(key) {
    if (!this.cache.has(key)) return null;
    
    const expiryTime = this.expiry.get(key);
    if (Date.now() > expiryTime) {
      this.cache.delete(key);
      this.expiry.delete(key);
      return null;
    }
    
    return this.cache.get(key);
  }

  has(key) {
    return this.get(key) !== null;
  }

  clear() {
    this.cache.clear();
    this.expiry.clear();
  }

  // Get cached data or execute function and cache result
  async getOrSet(key, asyncFn, ttl = this.defaultTTL) {
    const cached = this.get(key);
    if (cached !== null) {
      return cached;
    }

    try {
      const result = await asyncFn();
      this.set(key, result, ttl);
      return result;
    } catch (error) {
      throw error;
    }
  }
}

export const cacheService = new CacheService();