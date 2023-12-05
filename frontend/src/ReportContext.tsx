import { createContext, useState, useContext, useEffect } from 'react';
import { socket } from './socket';
import configData from './config.json';

export const ReportContext = createContext(null);

export const useReport = () => useContext(ReportContext);

export const ReportProvider = ({ children }) => {
    const [dataPoints, setDataPoints] = useState<{ timestamp: any; t2_stat: number; anomaly: number; }[]>([]);
    const [faultHistory, setFaultHistory] = useState([]);

    useEffect(() => {
        const handleT2Update = async (data: { timestamp: any; t2_stat: number; anomaly: boolean; }) => {
            const localtimestamp = new Date(data.timestamp).toLocaleTimeString();
            setDataPoints((prevDataPoints) => [
                ...prevDataPoints,
                { timestamp: localtimestamp, t2_stat: data.t2_stat, anomaly: data.anomaly ? data.t2_stat : 0 },
            ]);
            // console.log(data);
            if (data.anomaly) {
                const response = await fetch(`${configData.SERVER_URL}/fault_history`);
                const faultHistoryData = await response.json();
                setFaultHistory(faultHistoryData);
            }
        };

        socket.on('t2_update', handleT2Update);

        return () => {
            socket.off('t2_update', handleT2Update);
        };
    }, []);

    return (
        <ReportContext.Provider value={{ dataPoints, setDataPoints, faultHistory, setFaultHistory }}>
            {children}
        </ReportContext.Provider>
    )
}