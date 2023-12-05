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
