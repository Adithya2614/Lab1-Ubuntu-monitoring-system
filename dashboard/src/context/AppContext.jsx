/**
 * AppContext — Global state management.
 * Theme, preferences, notifications, sidebar state.
 */

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

const AppContext = createContext();

export const AppProvider = ({ children }) => {
  // Theme
  const [theme, setTheme] = useState(() => localStorage.getItem('wmi-theme') || 'dark');
  // View mode
  const [viewMode, setViewMode] = useState(() => localStorage.getItem('wmi-viewmode') || 'grid');
  // Sidebar
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [sidebarMobileOpen, setSidebarMobileOpen] = useState(false);
  // Modal
  const [isAddPCModalOpen, setIsAddPCModalOpen] = useState(false);
  // Notifications
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);

  // Persist theme
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('wmi-theme', theme);
  }, [theme]);

  // Persist view mode
  useEffect(() => {
    localStorage.setItem('wmi-viewmode', viewMode);
  }, [viewMode]);

  const toggleTheme = useCallback(() => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
  }, []);

  const addNotification = useCallback((notification) => {
    const id = Date.now();
    setNotifications(prev => [{ id, timestamp: new Date(), ...notification }, ...prev].slice(0, 50));
    setUnreadCount(prev => prev + 1);
  }, []);

  const clearUnread = useCallback(() => setUnreadCount(0), []);

  return (
    <AppContext.Provider value={{
      theme, toggleTheme,
      viewMode, setViewMode,
      sidebarCollapsed, setSidebarCollapsed,
      sidebarMobileOpen, setSidebarMobileOpen,
      isAddPCModalOpen, setIsAddPCModalOpen,
      notifications, addNotification, unreadCount, clearUnread,
    }}>
      {children}
    </AppContext.Provider>
  );
};

export const useAppContext = () => useContext(AppContext);
