import { useEffect, useRef } from 'react';
import axios from 'axios';

/**
 * Hook to keep the Render backend alive by making periodic requests
 * This prevents the free tier from spinning down after 15 minutes of inactivity
 * 
 * Strategy:
 * - Ping every 5 minutes automatically (Render timeout is 15 min)
 * - Also ping on user activity (click, mousemove, keyboard) to keep app responsive while in use
 * 
 * Usage in a component:
 * useKeepAlive();
 */
export const useKeepAlive = () => {
  const keepAliveTimeoutRef = useRef(null);
  const lastPingRef = useRef(0);

  const sendKeepAlivePing = async () => {
    try {
      // Railway doesn't need keep-alive (always running, not serverless)
      // Skip the ping to avoid CORS errors
      console.log('✅ Keep-alive disabled for Railway');
      lastPingRef.current = Date.now();
    } catch (error) {
      console.error('❌ Keep-alive ping failed:', error.message);
    }
  };

  useEffect(() => {
    // Ping immediately on app load
    sendKeepAlivePing();

    // Set up interval for periodic pings (every 5 minutes)
    const keepAliveInterval = setInterval(() => {
      sendKeepAlivePing();
    }, 5 * 60 * 1000); // 5 minutes

    // Listen for user activity - ping if we haven't pinged in 3 minutes
    const handleUserActivity = () => {
      const now = Date.now();
      const timeSinceLastPing = now - lastPingRef.current;
      
      // Only ping if it's been more than 3 minutes since last ping
      if (timeSinceLastPing > 3 * 60 * 1000) {
        console.log('🔄 User activity detected, sending keep-alive ping');
        sendKeepAlivePing();
      }
    };

    // Add activity listeners
    const events = ['click', 'mousemove', 'keydown', 'scroll', 'touchstart'];
    events.forEach(event => {
      document.addEventListener(event, handleUserActivity);
    });

    // Cleanup
    return () => {
      clearInterval(keepAliveInterval);
      if (keepAliveTimeoutRef.current) {
        clearTimeout(keepAliveTimeoutRef.current);
      }
      events.forEach(event => {
        document.removeEventListener(event, handleUserActivity);
      });
    };
  }, []);
};

export default useKeepAlive;
