import { createContext, useState, useContext, useEffect } from 'react';
import { socket } from './socket';

export const PlotContext = createContext(null);

export const usePlot = () => useContext(PlotContext);

export const PlotProvider = ({ children }) => {
    const [dataSeries, setDataSeries] = useState({});
    const [selectedSeries, setSelectedSeries] = useState([]);
    const [deselectedKeys, setDeselectedKeys] = useState([]);
    const MAX_POINTS = 30;

    useEffect(() => {
        socket.on('data_update', (message) => {
            // console.log(message);
            const newDataPoint = JSON.parse(message.data)
            const timestamp = new Date(newDataPoint.timestamp).toLocaleTimeString();
            delete newDataPoint.timestamp; // Remove timestamp from data point
            setDataSeries(prevData => {
                const updatedData = { ...prevData };
                Object.keys(newDataPoint).forEach(key => {
                    if (!updatedData[key]) {
                        updatedData[key] = [];
                    }
                    updatedData[key].push({ time: timestamp, value: newDataPoint[key] });
                    if (updatedData[key].length > MAX_POINTS) {
                        updatedData[key].shift();
                    }
                    if (!selectedSeries.includes(key) && !deselectedKeys.includes(key)) {
                        setSelectedSeries(prevSelected => [...prevSelected, key]);
                    }
                });
                return updatedData;
            });
        });

        return () => {
            socket.off('data_update');
        };
    }, [dataSeries, selectedSeries]);

    // Add any other functions or logic you need to manage the data series

    return (
        <PlotContext.Provider value={{ dataSeries, setDataSeries, selectedSeries, setSelectedSeries, deselectedKeys, setDeselectedKeys }}>
            {children}
        </PlotContext.Provider>
    );
};
