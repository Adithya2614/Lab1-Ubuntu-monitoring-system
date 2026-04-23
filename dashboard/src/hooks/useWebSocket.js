/**
 * useWebSocket — Socket.IO connection manager.
 * Handles connect, disconnect, auto-reconnect, and event listeners.
 */

import { useEffect, useRef, useCallback } from 'react';
import { io } from 'socket.io-client';
import { useAppContext } from '../context/AppContext';

export function useWebSocket() {
  const socketRef = useRef(null);
  const { addNotification } = useAppContext();

  useEffect(() => {
    const socket = io(window.location.origin, {
      path: '/ws/socket.io',
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionDelay: 2000,
    });

    socket.on('connect', () => console.log('🔌 WebSocket connected'));
    socket.on('disconnect', () => console.log('🔌 WebSocket disconnected'));

    socket.on('toast', (data) => {
      addNotification({ type: data.type || 'info', message: data.message });
    });

    socketRef.current = socket;

    return () => { socket.disconnect(); };
  }, [addNotification]);

  const on = useCallback((event, handler) => {
    socketRef.current?.on(event, handler);
    return () => socketRef.current?.off(event, handler);
  }, []);

  return { socket: socketRef, on };
}
