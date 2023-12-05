import { useState, useEffect } from 'react';
import { NavLink, Box } from '@mantine/core';
import { Link, useLocation } from 'react-router-dom';
import { NavbarProps } from '../types/nav';

export function NavbarSimple({ data }: NavbarProps) {
    const [active, setActive] = useState(-1);
    const location = useLocation();

    useEffect(() => {
        const activeIndex = data.findIndex(item => item.link === location.pathname);
        setActive(activeIndex >= 0 ? activeIndex : 0);
    }, [location]);

    const links = data.map((item, index) => (
        <NavLink
            key={item.label}
            label={item.label}
            component={Link}
            to={item.link}
            active={index === active}
            onClick={() => setActive(index)}

        />
    ));

    return (
        <Box>{links}</Box>
    );
}