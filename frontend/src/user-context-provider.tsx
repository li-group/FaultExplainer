import { useState } from 'react';
import { GlobalStateContext } from './user-context';

export const GlobalStateProvider = ({ children }: { children: React.ReactNode }) => {
    const [chatMessages, setChatMessages] = useState<any[]>([]);

    const contextValue = {
        chatMessages,
        setChatMessages,
    };

    return (
        <GlobalStateContext.Provider value={contextValue}>
            {children}
        </GlobalStateContext.Provider>
    );
};