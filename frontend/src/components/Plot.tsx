import { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export const ChartingComponent = ({ data, valueKey }) => {
    // console.log(data);
    // console.log(valueKey);
    const [chartKey, setChartKey] = useState(0);

    useEffect(() => {
        // When data is updated, reset the key to force re-render
        setChartKey(prevKey => prevKey + 1);
    }, [data]);
    const viewportHeight = window.innerHeight;
    const chartHeight = viewportHeight * 0.2;

    return (
        <div style={{ height: chartHeight }}>
            <ResponsiveContainer key={chartKey} width="100%" height="100%">
                <LineChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis domain={['auto', 'auto']} />
                    <Line type="step" dataKey="value" stroke="#8884d8" dot={false} isAnimationActive={false} />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
};

