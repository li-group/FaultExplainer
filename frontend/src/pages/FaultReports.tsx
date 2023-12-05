import { ComposedChart, Area, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart } from 'recharts';
import { Accordion } from '@mantine/core';
import ReactMarkdown from 'react-markdown';
import { Text, SimpleGrid } from '@mantine/core';
import { useReport } from '../ReportContext';

export function FaultReports() {
    const { dataPoints, setDataPoints, faultHistory, setFaultHistory } = useReport();

    console.log(faultHistory);
    return (
        <div>
            <ResponsiveContainer width="95%" height={200}>
                <Text size="xl" ta="center">T^2 Statistic</Text>
                <ComposedChart data={dataPoints}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                    <XAxis dataKey="timestamp" />
                    <YAxis />
                    {/* <Tooltip /> */}
                    <Line type="step" dataKey="t2_stat" stroke="#8884d8" dot={false} isAnimationActive={false} />
                    <Area type="step" dataKey="anomaly" stroke="#82ca9d" fill="#eb7575" isAnimationActive={false} />
                    {/* <Brush dataKey='timestamp' height={30} stroke="#8884d8" startIndex={startIndex} endIndex={endIndex} onChange={handleBrushChange} /> */}
                </ComposedChart>
            </ResponsiveContainer>
            <Accordion style={{ backgroundColor: '#f5f5f5' }}>
                {faultHistory.map((fault, index) => (
                    <Accordion.Item key={index} value={`Fault ${index + 1}`}>
                        <Accordion.Control>{`Fault @ ${new Date(fault.start_time).toLocaleString()}`}</Accordion.Control>
                        <Accordion.Panel>
                            <h3>Start Time:</h3>
                            <p>{new Date(fault.start_time).toLocaleString()}</p>
                            <h3>Explanation:</h3>
                            <SimpleGrid cols={3}>
                                {
                                    Object.keys(JSON.parse(fault.top_features)).map((key, index) => {
                                        const data = JSON.parse(fault.top_features)[key];
                                        return (
                                            <div key={index}>
                                                <Text ta="center">{key}</Text>
                                                <ResponsiveContainer width="95%" height={200} >
                                                    <LineChart data={data} >
                                                        <CartesianGrid strokeDasharray="3 3" vertical={false} />
                                                        <XAxis dataKey="timestamp" tickFormatter={(tickItem) => new Date(tickItem).toLocaleTimeString()} />
                                                        {/* <Label value={key} offset={0} position="top" /> */}
                                                        <YAxis domain={['auto', 'auto']} />
                                                        {/* <Tooltip /> */}
                                                        <Line type="step" dataKey="value" stroke="#8884d8" dot={false} isAnimationActive={false} />
                                                    </LineChart>
                                                </ResponsiveContainer>
                                            </div>
                                        )
                                    })
                                }
                            </SimpleGrid>
                            <ReactMarkdown>{fault.explanation}</ReactMarkdown>
                        </Accordion.Panel>
                    </Accordion.Item>
                ))}
            </Accordion>
        </div>
    );
};
