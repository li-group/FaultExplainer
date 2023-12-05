import { useDisclosure } from '@mantine/hooks';
import { AppShell, Burger } from '@mantine/core';
import { NavbarSimple } from './components/NavbarSimple';
import { Outlet } from 'react-router-dom';
import { NavItem } from './types/nav';
import { useEffect } from 'react';
import { ActionIcon } from '@mantine/core';
import { IconPlayerPlayFilled, IconPlayerPauseFilled } from '@tabler/icons-react';


const navData: NavItem[] = [
    { link: '/', label: 'Chat' },
    { link: '/plot', label: 'Plot' },
    { link: '/fault_reports', label: 'Fault Reports' },
];

import { useState } from 'react';
import { Text, Select, Slider } from '@mantine/core';

export function MyHeader() {
    const [selectedState, setSelectedState] = useState('Normal');
    const [rate, setRate] = useState(1.0);
    const [endValue, setEndValue] = useState<number>(1.0);
    const [isPaused, setIsPaused] = useState(false);

    useEffect(() => {
        // Fetch the initial state and rate values
        fetch('http://localhost:5000/get_state') // Replace with your server's URL
            .then(response => response.json())
            .then(data => setSelectedState(data.state === 0 ? 'Normal' : `Fault ${data.state}`));

        fetch('http://localhost:5000/get_rate') // Replace with your server's URL
            .then(response => response.json())
            .then(data => setRate(Number(data.rate)));
        console.log(rate);

        fetch('http://localhost:5000/get_pause_status') // Replace with your server's URL
            .then(response => response.json())
            .then(data => setIsPaused(data.status));
    }, []);

    const handlePauseResume = async () => {
        const endpoint = isPaused ? '/resume' : '/pause';
        // const response = await fetch(`http://localhost:5000${endpoint}`, { method: 'POST' });
        const response = await fetch(`http://localhost:5000${endpoint}`, { // Replace with your server's URL
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ state: isPaused })
        });
        const data = await response.json();
        console.log(data.message);
        setIsPaused(!isPaused);
    };


    const handleStateChange = async (value) => {
        setSelectedState(value);

        const state = value === 'Normal' ? 0 : parseInt(value.split(' ')[1]);

        // Send a POST request to the /change_state endpoint
        const response = await fetch('http://localhost:5000/change_state', { // Replace with your server's URL
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ state: state })
        });

        const data = await response.json();
        console.log(data.message);
    };

    const handleRateChange = async (value) => {
        setEndValue(value);

        // Send a POST request to the /set_rate endpoint
        const response = await fetch('http://localhost:5000/set_rate', { // Replace with your server's URL
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ rate: value })
        });

        const data = await response.json();
        console.log(data.message);
    };

    return (
        <div style={{ display: 'flex', justifyContent: 'space-between', padding: '1rem' }}>
            <Text size="xl" weight={500}>TEP-LLM</Text>
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', flexGrow: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', marginRight: '1rem' }}>
                    <Text size="md" style={{ marginRight: '0.5rem' }}>State:</Text>
                    <Select
                        style={{ width: '150px' }}
                        data={['Normal', ...Array.from({ length: 20 }, (_, i) => `Fault ${i + 1}`)]}
                        value={selectedState}
                        onChange={handleStateChange}
                        placeholder="Select state"
                    />
                </div>
                <div style={{ display: 'flex', alignItems: 'center' }}>
                    <Text size="md" style={{ marginRight: '0.5rem' }}>Rate:</Text>
                    <Slider
                        style={{ width: '150px' }}
                        min={0.1}
                        max={2}
                        step={0.1}
                        value={rate}
                        onChange={setRate}
                        onChangeEnd={handleRateChange}
                        label={rate.toFixed(1)}
                        labelAlwaysOn
                    />
                    <ActionIcon
                        variant={isPaused ? 'filled' : 'light'}
                        color={isPaused ? 'green' : 'red'}
                        onClick={handlePauseResume}
                        style={{ marginLeft: '1rem' }}
                    >
                        {isPaused ? <IconPlayerPlayFilled style={{ width: '70%', height: '70%' }} stroke={1.5} /> : <IconPlayerPauseFilled style={{ width: '70%', height: '70%' }} stroke={1.5} />}
                    </ActionIcon>
                </div>
            </div>
        </div >
    );
}

export function Layout() {
    const [opened, { toggle }] = useDisclosure();

    return (
        <AppShell
            header={{ height: 60 }}
            navbar={{ width: 300, breakpoint: 'sm', collapsed: { mobile: !opened } }}
            padding="md" >

            <AppShell.Header>
                <Burger opened={opened} onClick={toggle} hiddenFrom="sm" size="sm" />
                {/* <div>Logo</div> */}
                <MyHeader />
            </AppShell.Header>

            <AppShell.Navbar p="md">
                <NavbarSimple data={navData} />
            </AppShell.Navbar>

            <AppShell.Main>
                <Outlet />
            </AppShell.Main>
        </AppShell>
    );
}