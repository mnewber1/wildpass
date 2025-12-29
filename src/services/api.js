// Use environment variable if available, otherwise default to localhost:5001
const API_BASE_URL = typeof process !== 'undefined' && process.env && process.env.REACT_APP_API_URL
  ? process.env.REACT_APP_API_URL
  : 'http://localhost:5001/api';

// Cache utilities
const CACHE_PREFIX = 'wildpass_';
const CACHE_DURATION = 60 * 60 * 1000; // 1 hour in milliseconds

class CacheManager {
  static getCacheKey(origins, destinations, tripType, departureDate, returnDate) {
    // Don't sort arrays - maintain origin->destination order for cache key
    // This ensures that ORD->CUN and CUN->ORD are treated as different searches
    return `${CACHE_PREFIX}${origins.join(',')}_${destinations.join(',')}_${tripType}_${departureDate}_${returnDate || 'null'}`;
  }

  static setCache(key, data) {
    try {
      const cacheEntry = {
        data,
        timestamp: Date.now(),
      };
      localStorage.setItem(key, JSON.stringify(cacheEntry));
    } catch (error) {
      console.error('Error setting cache:', error);
    }
  }

  static getCache(key) {
    try {
      const cached = localStorage.getItem(key);
      if (!cached) return null;

      const cacheEntry = JSON.parse(cached);
      const age = Date.now() - cacheEntry.timestamp;

      // Check if cache is still valid
      if (age < CACHE_DURATION) {
        return cacheEntry.data;
      }

      // Cache expired, remove it
      localStorage.removeItem(key);
      return null;
    } catch (error) {
      console.error('Error reading cache:', error);
      return null;
    }
  }

  static clearCache() {
    try {
      const keys = Object.keys(localStorage);
      keys.forEach(key => {
        if (key.startsWith(CACHE_PREFIX)) {
          localStorage.removeItem(key);
        }
      });
    } catch (error) {
      console.error('Error clearing cache:', error);
    }
  }

  static getCacheStats() {
    try {
      const keys = Object.keys(localStorage);
      const cacheKeys = keys.filter(key => key.startsWith(CACHE_PREFIX));
      let validCount = 0;
      let expiredCount = 0;

      cacheKeys.forEach(key => {
        const cached = localStorage.getItem(key);
        if (cached) {
          const cacheEntry = JSON.parse(cached);
          const age = Date.now() - cacheEntry.timestamp;
          if (age < CACHE_DURATION) {
            validCount++;
          } else {
            expiredCount++;
          }
        }
      });

      return {
        total: cacheKeys.length,
        valid: validCount,
        expired: expiredCount,
      };
    } catch (error) {
      console.error('Error getting cache stats:', error);
      return { total: 0, valid: 0, expired: 0 };
    }
  }
}

// API functions

// Streaming search with EventSource (Server-Sent Events)
export const searchFlightsStreaming = (searchParams, onFlights, onComplete, onError) => {
  const { origins, destinations, tripType, departureDate, returnDate } = searchParams;

  // Check cache first
  const cacheKey = CacheManager.getCacheKey(origins, destinations, tripType, departureDate, returnDate);
  console.log('🔑 Cache key:', cacheKey);
  console.log('📋 Search params:', { origins, destinations, tripType, departureDate, returnDate });

  const cachedData = CacheManager.getCache(cacheKey);

  if (cachedData) {
    console.log('✅ Returning cached flight data');
    // Return cached data immediately
    if (cachedData.flights) {
      onFlights(cachedData.flights);
    }
    if (onComplete) {
      onComplete({ total: cachedData.flights?.length || 0, fromCache: true });
    }
    return;
  }

  console.log('🌐 Fetching fresh data from API');

  // Use fetch with stream for SSE
  fetch(`${API_BASE_URL}/search/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(searchParams),
  })
    .then(response => {
      if (!response.ok) {
        throw new Error(`API error: ${response.status} ${response.statusText}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      const allFlights = [];

      const processText = ({ done, value }) => {
        if (done) {
          console.log('Stream complete');
          return;
        }

        // Decode the chunk and add to buffer
        buffer += decoder.decode(value, { stream: true });

        // Process complete lines from buffer
        const lines = buffer.split('\n');
        buffer = lines.pop() || ''; // Keep incomplete line in buffer

        lines.forEach(line => {
          if (line.startsWith('data: ')) {
            try {
              const jsonStr = line.substring(6);
              const event = JSON.parse(jsonStr);

              if (event.complete) {
                // Search complete
                console.log(`Search complete: ${event.total_flights} flights`);

                // Cache all results
                CacheManager.setCache(cacheKey, { flights: allFlights });

                if (onComplete) {
                  onComplete({ total: event.total_flights, fromCache: false });
                }
              } else if (event.flights) {
                // New flights received for a route
                console.log(`Received ${event.count} flights for ${event.route}`);
                allFlights.push(...event.flights);
                onFlights(event.flights);
              }
            } catch (e) {
              console.error('Error parsing SSE event:', e);
            }
          }
        });

        // Continue reading
        return reader.read().then(processText);
      };

      return reader.read().then(processText);
    })
    .catch(error => {
      console.error('Error in streaming search:', error);
      if (onError) {
        onError(error);
      }
    });
};

// Regular search (non-streaming, for compatibility)
export const searchFlights = async (searchParams) => {
  const { origins, destinations, tripType, departureDate, returnDate } = searchParams;

  // Check cache first
  const cacheKey = CacheManager.getCacheKey(origins, destinations, tripType, departureDate, returnDate);
  const cachedData = CacheManager.getCache(cacheKey);

  if (cachedData) {
    console.log('Returning cached flight data');
    return {
      ...cachedData,
      fromCache: true,
    };
  }

  // Make API request
  try {
    const response = await fetch(`${API_BASE_URL}/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(searchParams),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();

    // Cache the results
    CacheManager.setCache(cacheKey, data);

    return {
      ...data,
      fromCache: false,
    };
  } catch (error) {
    console.error('Error searching flights:', error);
    throw error;
  }
};

export const getDestinations = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/destinations`);

    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching destinations:', error);
    throw error;
  }
};

export const healthCheck = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);

    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error checking API health:', error);
    throw error;
  }
};

export const clearServerCache = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/cache/clear`, {
      method: 'POST',
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error clearing server cache:', error);
    throw error;
  }
};

export const getCacheStats = () => {
  return CacheManager.getCacheStats();
};

export const clearLocalCache = () => {
  CacheManager.clearCache();
};

// Trip Planner API
export const planTrip = async (searchParams) => {
  try {
    const response = await fetch(`${API_BASE_URL}/trip-planner`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(searchParams),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error planning trip:', error);
    throw error;
  }
};
