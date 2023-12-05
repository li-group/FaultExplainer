// import { useState, useEffect } from 'react';
// import { Text, SimpleGrid, Group } from '@mantine/core';
// import { Chip, Drawer, ActionIcon, Button } from '@mantine/core';
// import { ChartingComponent } from '../components/Plot';
// import { socket } from '../socket';
// import { IconAdjustments } from '@tabler/icons-react';


// export function PlotPage() {
//     const [dataSeries, setDataSeries] = useState({});
//     const [selectedSeries, setSelectedSeries] = useState([]);
//     const [deselectedKeys, setDeselectedKeys] = useState([]);
//     const [isDrawerOpen, setDrawerOpen] = useState(false);
//     const MAX_POINTS = 30;


//     useEffect(() => {
//         socket.on('data_update', (message) => {
//             // console.log(message);
//             const newDataPoint = JSON.parse(message.data)
//             const timestamp = new Date(newDataPoint.timestamp).toLocaleTimeString();
//             delete newDataPoint.timestamp; // Remove timestamp from data point
//             setDataSeries(prevData => {
//                 const updatedData = { ...prevData };
//                 Object.keys(newDataPoint).forEach(key => {
//                     if (!updatedData[key]) {
//                         updatedData[key] = [];
//                     }
//                     updatedData[key].push({ time: timestamp, value: newDataPoint[key] });
//                     if (updatedData[key].length > MAX_POINTS) {
//                         updatedData[key].shift();
//                     }
//                     if (!selectedSeries.includes(key) && !deselectedKeys.includes(key)) {
//                         setSelectedSeries(prevSelected => [...prevSelected, key]);
//                     }
//                 });
//                 return updatedData;
//             });
//         });

//         return () => {
//             socket.off('data_update');
//         };
//     }, [dataSeries, selectedSeries]);

//     const handleChipChange = (newSelectedSeries) => {
//         const newlyDeselectedKeys = selectedSeries.filter(key => !newSelectedSeries.includes(key));
//         setDeselectedKeys(prevDeselectedKeys => [...prevDeselectedKeys, ...newlyDeselectedKeys]);
//         setSelectedSeries(newSelectedSeries);
//     };

//     const selectAll = () => {
//         setSelectedSeries(Object.keys(dataSeries));
//         setDeselectedKeys([]); // Clear deselectedKeys when all keys are selected
//     };

//     const deselectAll = () => {
//         setSelectedSeries([]);
//         setDeselectedKeys(Object.keys(dataSeries)); // Add all keys to deselectedKeys when all keys are deselected
//     };

//     return (
//         <div>
//             <ActionIcon variant="default" aria-label="Settings" onClick={() => setDrawerOpen(true)}>
//                 <IconAdjustments style={{ width: '70%', height: '70%' }} stroke={1.5} />
//             </ActionIcon>

//             <Drawer opened={isDrawerOpen} onClose={() => setDrawerOpen(false)} padding="md" size="xs" title="Select Graphs">
//                 <Button onClick={selectAll}>Select All</Button>
//                 <Button onClick={deselectAll}>Deselect All</Button>
//                 <Chip.Group multiple value={selectedSeries} onChange={handleChipChange}>
//                     <Group justify='left' mt='md'>
//                         {Object.keys(dataSeries).map(key => (
//                             <Chip value={key} >
//                                 {key}
//                             </Chip>
//                         ))}
//                     </Group>
//                 </Chip.Group>
//             </Drawer>

//             <SimpleGrid cols={5} style={{ margin: "0 30px 0 0" }}>
//                 {Object.keys(dataSeries).map(key => {
//                     if (!selectedSeries.includes(key)) return null;
//                     return (
//                         <div key={key}>
//                             <Text ta="center">{key}</Text>
//                             <ChartingComponent data={dataSeries[key]} valueKey={key} />
//                         </div>
//                     )
//                 })}
//             </SimpleGrid>
//         </div>
//     );
// }

// export default PlotPage;


import { useState, useEffect } from 'react';
import { Text, SimpleGrid, Group } from '@mantine/core';
import { Chip, Drawer, ActionIcon, Button } from '@mantine/core';
import { ChartingComponent } from '../components/Plot';
import { IconAdjustments } from '@tabler/icons-react';
import { usePlot } from '../PlotContext';



export function PlotPage() {
    const { dataSeries, setDataSeries, selectedSeries, setSelectedSeries, deselectedKeys, setDeselectedKeys } = usePlot();
    // const [dataSeries, setDataSeries] = useState({});
    // const [selectedSeries, setSelectedSeries] = useState([]);
    // const [deselectedKeys, setDeselectedKeys] = useState([]);
    const [isDrawerOpen, setDrawerOpen] = useState(false);



    const handleChipChange = (newSelectedSeries) => {
        const newlyDeselectedKeys = selectedSeries.filter(key => !newSelectedSeries.includes(key));
        setDeselectedKeys(prevDeselectedKeys => [...prevDeselectedKeys, ...newlyDeselectedKeys]);
        setSelectedSeries(newSelectedSeries);
    };

    const selectAll = () => {
        setSelectedSeries(Object.keys(dataSeries));
        setDeselectedKeys([]); // Clear deselectedKeys when all keys are selected
    };

    const deselectAll = () => {
        setSelectedSeries([]);
        setDeselectedKeys(Object.keys(dataSeries)); // Add all keys to deselectedKeys when all keys are deselected
    };

    return (
        <div>
            <ActionIcon variant="default" aria-label="Settings" onClick={() => setDrawerOpen(true)}>
                <IconAdjustments style={{ width: '70%', height: '70%' }} stroke={1.5} />
            </ActionIcon>

            <Drawer opened={isDrawerOpen} onClose={() => setDrawerOpen(false)} padding="md" size="xs" title="Select Graphs">
                <Button onClick={selectAll}>Select All</Button>
                <Button onClick={deselectAll}>Deselect All</Button>
                <Chip.Group multiple value={selectedSeries} onChange={handleChipChange}>
                    <Group justify='left' mt='md'>
                        {Object.keys(dataSeries).map(key => (
                            <Chip value={key} >
                                {key}
                            </Chip>
                        ))}
                    </Group>
                </Chip.Group>
            </Drawer>

            <SimpleGrid cols={5} style={{ margin: "0 30px 0 0" }}>
                {Object.keys(dataSeries).map(key => {
                    if (!selectedSeries.includes(key)) return null;
                    return (
                        <div key={key}>
                            <Text ta="center">{key}</Text>
                            <ChartingComponent data={dataSeries[key]} valueKey={key} />
                        </div>
                    )
                })}
            </SimpleGrid>
        </div>
    );
}

export default PlotPage;
