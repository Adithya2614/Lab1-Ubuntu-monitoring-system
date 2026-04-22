import React, { createContext, useContext, useState } from 'react';

const AppContext = createContext();

export const AppProvider = ({ children }) => {
    const [viewMode, setViewMode] = useState('grid'); // grid | list
    const [isAddPCModalOpen, setIsAddPCModalOpen] = useState(false);

    return (
        <AppContext.Provider value={{ viewMode, setViewMode, isAddPCModalOpen, setIsAddPCModalOpen }}>
            {children}
        </AppContext.Provider>
    );
};

export const useAppContext = () => useContext(AppContext);
