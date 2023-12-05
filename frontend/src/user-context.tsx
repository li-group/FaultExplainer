import { createContext } from 'react';

export const GlobalStateContext = createContext({
    chatMessages: [],
    setChatMessages: (messages: any[]) => { },
});