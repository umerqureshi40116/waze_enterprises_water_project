import { useEffect } from 'react';
import api from '../api/axios';

/**
 * Hook to keep the Render backend alive by making periodic requests
 * This prevents the free tier from spinning down after 15 minutes of inactivity
 * 
 * Usage in a component:
 * useKeepAlive();
 */
export const useKeepAlive = () => {
  useEffect(() => {
    // Call keep-alive endpoint every 10 minutes
    const keepAliveInterval = setInterval(async () => {
      try {
        await api.get('/keep-alive');
        console.log('✅ Keep-alive ping sent to backend');
      } catch (error) {
        console.error('❌ Keep-alive ping failed:', error);
        // Don't log too many errors, just silently retry
      }
    }, 10 * 60 * 1000); // 10 minutes

    // Also ping on app load
    const pingOnLoad = async () => {
      try {
        await api.get('/keep-alive');
        console.log('✅ Initial keep-alive ping sent');
      } catch (error) {
        console.error('Keep-alive error:', error);
      }
    };
    pingOnLoad();

    // Cleanup interval on unmount
    return () => clearInterval(keepAliveInterval);
  }, []);
};

export default useKeepAlive;
