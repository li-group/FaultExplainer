// Define the type for a navigation item
export type NavItem = {
    link: string;
    label: string;
};

// Define the type for Navbar props
export type NavbarProps = {
    data: NavItem[];
};
