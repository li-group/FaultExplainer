import React, { useState, useEffect, createContext, useContext } from "react";
import { Outlet, Link, useLocation } from "react-router-dom";
import Papa from "papaparse";
import {
  ActionIcon,
  AppShell,
  Box,
  Burger,
  Group,
  NavLink,
  Select,
  Slider,
  Text,
} from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import intro_image from "./assets/intro.json";
import {
  IconPlayerPauseFilled,
  IconPlayerPlayFilled,
  IconChartHistogram,
  IconRobot,
  IconReport,
} from "@tabler/icons-react";
import { fetchEventSource } from "@microsoft/fetch-event-source";
import fs from 'fs';
import path from 'path';

// CONSTANTS
const fileId2fileName = [
  "./fault0.csv",
  "./fault1.csv",
  "./fault2.csv",
  "./fault3.csv",
  "./fault4.csv",
  "./fault5.csv",
  "./fault6.csv",
  "./fault7.csv",
  "./fault8.csv",
  "./fault9.csv",
  "./fault10.csv",
  "./fault11.csv",
  "./fault12.csv",
  "./fault13.csv",
  "./fault14.csv",
  "./fault15.csv",
  "./fault16.csv",
  "./fault17.csv",
  "./fault18.csv",
  "./fault19.csv",
  "./fault20.csv",
];

const fault_name = [
  "Normal Operation",
  "Step change in A/C feed ratio, B composition constant (stream 4)",
  "Step change in B composition, A/C ratio constant (stream 4)",
  "Step change in D feed temperature (stream 2)",
  "Step change in Reactor cooling water inlet temperature",
  "Step change in Condenser cooling water inlet temperature",
  "Step change in A feed loss (stream 1)",
  "Step change in C header pressure loss-reduced availability (stream 4)",
  "Random variation in A, B, C feed composition (stream 4)",
  "Random variation in D feed temperature (stream 2)",
  "Random variation in C feed temperature (stream 4)",
  "Random variation in Reactor cooling water inlet temperature",
  "Random variation in Condenser cooling water inlet temperature",
  "Slow drift in Reaction kinetics",
  "Sticking Reactor cooling water valve",
  "Sticking Condenser cooling water valve",
  "Unknown (16)",
  "Unknown (17)",
  "Unknown (18)",
  "Unknown (19)",
  "Unknown (20)",
  // 'Constant position for the valve for stream 4',
];

// eslint-disable-next-line react-refresh/only-export-components
export const columnFilter: string[] = [
  // "time",
  "A Feed",
  "D Feed",
  "E Feed",
  "A and C Feed",
  "Recycle Flow",
  "Reactor Feed Rate",
  "Reactor Pressure",
  "Reactor Level",
  "Reactor Temperature",
  "Purge Rate",
  "Product Sep Temp",
  "Product Sep Level",
  "Product Sep Pressure",
  "Product Sep Underflow",
  "Stripper Level",
  "Stripper Pressure",
  "Stripper Underflow",
  "Stripper Temp",
  "Stripper Steam Flow",
  "Compressor Work",
  "Reactor Coolant Temp",
  "Separator Coolant Temp",
  "Component A to Reactor",
  "Component B to Reactor",
  "Component C to Reactor",
  "Component D to Reactor",
  "Component E to Reactor",
  "Component F to Reactor",
  "Component A in Purge",
  "Component B in Purge",
  "Component C in Purge",
  "Component D in Purge",
  "Component E in Purge",
  "Component F in Purge",
  "Component G in Purge",
  "Component H in Purge",
  "Component D in Product",
  "Component E in Product",
  "Component F in Product",
  "Component G in Product",
  "Component H in Product",
  "D feed load",
  "E feed load",
  "A feed load",
  "A and C feed load",
  "Compressor recycle valve",
  "Purge valve",
  "Separator liquid load",
  "Stripper liquid load",
  "Stripper steam valve",
  "Reactor coolant load",
  "Condenser coolant load",
];

// eslint-disable-next-line react-refresh/only-export-components
export const columnFilterUnits: Record<string, string> = {
  // time: "min",
  "A Feed": "kscmh",
  "D Feed": "kg/hr",
  "E Feed": "kg/hr",
  "A and C Feed": "kscmh",
  "Recycle Flow": "kscmh",
  "Reactor Feed Rate": "kscmh",
  "Reactor Pressure": "kPa gauge",
  "Reactor Level": "%",
  "Reactor Temperature": "Deg C",
  "Purge Rate": "kscmh",
  "Product Sep Temp": "Deg C",
  "Product Sep Level": "%",
  "Product Sep Pressure": "kPa gauge",
  "Product Sep Underflow": "m3/hr",
  "Stripper Level": "%",
  "Stripper Pressure": "kPa gauge",
  "Stripper Underflow": "m3/hr",
  "Stripper Temp": "Deg C",
  "Stripper Steam Flow": "kg/hr",
  "Compressor Work": "kW",
  "Reactor Coolant Temp": "Deg C",
  "Separator Coolant Temp": "Deg C",
  "Component A to Reactor": "mole %",
  "Component B to Reactor": "mole %",
  "Component C to Reactor": "mole %",
  "Component D to Reactor": "mole %",
  "Component E to Reactor": "mole %",
  "Component F to Reactor": "mole %",
  "Component A in Purge": "mole %",
  "Component B in Purge": "mole %",
  "Component C in Purge": "mole %",
  "Component D in Purge": "mole %",
  "Component E in Purge": "mole %",
  "Component F in Purge": "mole %",
  "Component G in Purge": "mole %",
  "Component H in Purge": "mole %",
  "Component D in Product": "mole %",
  "Component E in Product": "mole %",
  "Component F in Product": "mole %",
  "Component G in Product": "mole %",
  "Component H in Product": "mole %",
  "D feed load": "mole %",
  "E feed load": "mole %",
  "A feed load": "mole %",
  "A and C feed load": "mole %",
  "Compressor recycle valve": "mole %",
  "Purge valve": "mole %",
  "Separator liquid load": "mole %",
  "Stripper liquid load": "mole %",
  "Stripper steam valve": "mole %",
  "Reactor coolant load": "mole %",
  "Condenser coolant load": "mole %",
};

console.log("columnFilter: ", columnFilter);
console.log("columnFilterUnits: ", columnFilterUnits);

const importanceFilter: string[] = [
  "t2_A Feed",
  "t2_D Feed",
  "t2_E Feed",
  "t2_A and C Feed",
  "t2_Recycle Flow",
  "t2_Reactor Feed Rate",
  "t2_Reactor Pressure",
  "t2_Reactor Level",
  "t2_Reactor Temperature",
  "t2_Purge Rate",
  "t2_Product Sep Temp",
  "t2_Product Sep Level",
  "t2_Product Sep Pressure",
  "t2_Product Sep Underflow",
  "t2_Stripper Level",
  "t2_Stripper Pressure",
  "t2_Stripper Underflow",
  "t2_Stripper Temp",
  "t2_Stripper Steam Flow",
  "t2_Compressor Work",
  "t2_Reactor Coolant Temp",
  "t2_Separator Coolant Temp",
  "t2_Component A to Reactor",
  "t2_Component B to Reactor",
  "t2_Component C to Reactor",
  "t2_Component D to Reactor",
  "t2_Component E to Reactor",
  "t2_Component F to Reactor",
  "t2_Component A in Purge",
  "t2_Component B in Purge",
  "t2_Component C in Purge",
  "t2_Component D in Purge",
  "t2_Component E in Purge",
  "t2_Component F in Purge",
  "t2_Component G in Purge",
  "t2_Component H in Purge",
  "t2_Component D in Product",
  "t2_Component E in Product",
  "t2_Component F in Product",
  "t2_Component G in Product",
  "t2_Component H in Product",
  "t2_D feed load",
  "t2_E feed load",
  "t2_A feed load",
  "t2_A and C feed load",
  "t2_Compressor recycle valve",
  "t2_Purge valve",
  "t2_Separator liquid load",
  "t2_Stripper liquid load",
  "t2_Stripper steam valve",
  "t2_Reactor coolant load",
  "t2_Condenser coolant load",
];

const intro = `The process produces two products from four reactants. Also present are an inert and a byproduct making a total of eight components:
A, B, C, D, E, F, G, and H. The reactions are:

A(g) + C(g) + D(g) - G(liq): Product 1,

A(g) + C(g) + E(g) - H(liq): Product 2,

A(g) + E(g) - F(liq): Byproduct,

3D(g) - 2F(liq): Byproduct.

All the reactions are irreversible and exothermic. The reaction rates are a function of temperature through an Arrhenius expression.
The reaction to produce G has a higher activation energy resulting in more sensitivity to temperature.
Also, the reactions are approximately first-order with respect to the reactant concentrations.

The process has five major unit operations: the reactor, the product condenser, a vapor-liquid separator, a recycle compressor and a product stripper.
Figure showing a diagram of the process is attached.

The gaseous reactants are fed to the reactor where they react to form liquid products. The gas phase reactions are catalyzed by a nonvolatile catalyst dissolved
in the liquid phase. The reactor has an internal cooling bundle for removing the heat of reaction. The products leave the reactor as vapors along with the unreacted feeds.
The catalyst remains in the reactor. The reactor product stream passes through a cooler for condensing the products and from there to a vapor-liquid separator.
Noncondensed components recycle back through a centrifugal compressor to the reactor feed.
Condensed components move to a product stripping column to remove remaining reactants by stripping with feed stream number 4.
Products G and H exit the stripper base and are separated in a downstream refining section which is not included in this problem.
The inert and byproduct are primarily purged from the system as a vapor from the vapor-liquid separator.`;

// Read and parse the config.json file
// const configPath = path.resolve(__dirname, '../config.json');
// const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));

// // Extract the postFaultThreshold value
// const postFaultThreshold: number = config.fault_trigger_consecutive_step-1;
// const topkfeatures: number = config.topkfeatures;
const postFaultThreshold: number = 6-1;
const topkfeatures: number = 6;

// TYPES
type RowType = { [key: string]: string };
type CSVType = RowType[];
type Image = { image: string; name: string };
export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  text: string;
  images: Image[];
  explanation: boolean;
};
export type DataPointsId = { [key: string]: number[] };
type ChatContextId = {
  conversation: ChatMessage[];
  setConversation: React.Dispatch<React.SetStateAction<ChatMessage[]>>;
};
export type StatContextId = { t2_stat: number; anomaly: boolean; time: string };

interface SimulatorInterface {
  csvFile: string;
  interval: number;
  setCurrentRow: (row: RowType | null) => void;
  pause: boolean;
}

// CONTEXTS
const DataPointsContext = createContext<DataPointsId>({} as DataPointsId);
const ConservationContext = createContext<ChatContextId>({} as ChatContextId);
const StatContext = createContext<StatContextId[]>({} as StatContextId[]);

function Simulator({
  csvFile,
  interval,
  setCurrentRow,
  pause,
}: SimulatorInterface) {
  const [data, setData] = useState<CSVType>([]);
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    console.log("Simulator component mounted or csvFile changed");
    if (csvFile) {
      setCurrentIndex(0);
      console.log("inside simulator useEffect", csvFile);
      Papa.parse<RowType>(csvFile, {
        complete: (result) => {
          console.log("CSV file parsed:", result.data);
          setData(result.data);
        },
        header: true,
        download: true,
        skipEmptyLines: "greedy",
        transformHeader: (header) => header.trim(),
        transform: (value) => value.trim(),
      });
    }
  }, [csvFile]);

  useEffect(() => {
    if (data.length > 0 && !pause) {
      // console.log('Starting interval to update current row');
      const timer = setInterval(() => {
        setCurrentRow(data[currentIndex]);
        setCurrentIndex((prevIndex) => (prevIndex + 1) % data.length);
      }, interval);

      return () => {
        // console.log('Clearing interval');
        clearInterval(timer);
      }; // Cleanup interval on component unmount
    }
  }, [data, currentIndex, interval, setCurrentRow, pause]);

  return null; // This component doesn't render anything
}

// eslint-disable-next-line react-refresh/only-export-components
export const startTime = new Date();

function getTopKElements(datapoints: DataPointsId, topK: number) {
  // Step 1: Filter the columns based on importance_filter
  const filteredData: DataPointsId = {};
  for (const key of importanceFilter) {
    console.log("Key", key);
    if (datapoints[key]) {
      filteredData[key] = datapoints[key];
    }
  }

  // Step 2: Retrieve the last element of the arrays for the filtered columns
  const lastElements: { [key: string]: number } = {};
  for (const key in filteredData) {
    lastElements[key] = filteredData[key][filteredData[key].length - 1];
    console.log("lastElements", lastElements);
  }

  // Step 3: Find the top K elements based on these last elements
  const sortedKeys = Object.keys(lastElements).sort(
    (a, b) => lastElements[b] - lastElements[a]
  );
  const topKKeys = sortedKeys.slice(0, topK).map((a) => a.slice(3));
  console.log("topKKeys", topKKeys);

  return topKKeys;
}

export default function App() {
  const [opened, { toggle }] = useDisclosure();
  const [selectedFileId, setSelectedFileId] = useState<number>(0);
  const [sliderValue, setSliderValue] = useState(1); // Default interval of 1 second
  const [interval, setInterval] = useState(1); // Default interval of 1 second
  const [currentRow, setCurrentRow] = useState<RowType | null>(null);
  const [dataPoints, setDataPoints] = useState<DataPointsId>({});
  const [pause, setPause] = useDisclosure(false);
  const [t2_stat, setT2_stat] = useState<StatContextId[]>([]);
  const [currentFaultId, setCurrentFaultId] = useState<number | null>(null);
  const [prevFaultId, setPrevFaultId] = useState<number>(0);
  const [postFaultDataCount, setPostFaultDataCount] = useState<number>(0);
  const location = useLocation();
  const intro_msg: ChatMessage = {
    id: "intro",
    role: "assistant",
    text: intro,
    images: [intro_image],
    explanation: false,
  };
  const [conversation, setConversation] = useState<ChatMessage[]>([intro_msg]);
  // const [conversation, setConversation] = useState<ChatMessage[]>([]);

  const handleFileChange = (value: string | null) => {
    setSelectedFileId(fault_name.indexOf(value ?? fault_name[0]));
  };

  // UseEffect to log active file path after `selectedFileId` changes
  useEffect(() => {
    console.log("Active file path:", fileId2fileName[selectedFileId]);
  }, [selectedFileId]);

  
  async function sendFaultToBackend(
    fault: { [key: string]: number[] },
    id: string,
    filePath: string
  ) {
    console.log("Sending fault to backend with file:", filePath);
    console.log("check the datta", JSON.stringify({ data: fault, id: id, file: filePath }));
    const payload = {
      data: fault,
      id: id,
      file: filePath, // Include the filePath in the request payload
    };
    await fetchEventSource("http://localhost:8000/explain", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "text/event-stream",
      },
      body: JSON.stringify(payload),
      async onopen(res) {
        if (res.ok && res.status === 200) {
          console.log("Connection made ", res);
        } else if (res.status >= 400 && res.status < 500 && res.status !== 429) {
          console.log("Client-side error ", res);
        }
      },
      onmessage(event) {
        const parsedData = JSON.parse(event.data);
        setConversation((prevMessages) => {
          const index = prevMessages.findIndex(
            (message) => message.id === parsedData.id
          );
          if (index !== -1) {
            const updatedMessages = [...prevMessages];
            updatedMessages[index] = {
              ...updatedMessages[index],
              text: updatedMessages[index].text + parsedData.content,
            };
            return updatedMessages;
          } else {
            const newMessage: ChatMessage = {
              id: parsedData.id,
              role: "assistant",
              text: parsedData.content,
              images: parsedData.images,
              explanation: true,
            };
            return [...prevMessages, newMessage];
          }
        });
      },
      onclose() {
        console.log("Connection closed by the server");
      },
      onerror(err) {
        console.log("There was an error from server", err);
      },
    });
  }
  

  useEffect(() => {
    if (currentRow) {
      setDataPoints((prevDataPoints) => {
        const newDataPoints = { ...prevDataPoints };
        for (const [key, value] of Object.entries(currentRow)) {
          if (!newDataPoints[key]) {
            newDataPoints[key] = [];
          }
          const numValue = parseFloat(value); // Convert the string value to a number
          if (!isNaN(numValue)) {
            newDataPoints[key] = [...newDataPoints[key], numValue].slice(-30);
          }
        }
        return newDataPoints;
      });
      setT2_stat((data) => {
        if ("t2_stat" in currentRow && "anomaly" in currentRow) {
          const date = new Date(
            startTime.getTime() + (Number(currentRow.time) * 3 * 60000) / 0.05
          );
          const timeString = date.getHours() + ":" + date.getMinutes();

          return [
            ...data,
            {
              t2_stat: parseFloat(currentRow.t2_stat),
              anomaly: currentRow.anomaly === "True",
              time: timeString,
            },
          ];
        } else {
          return data;
        }
      });
      if (currentRow.anomaly === "True") {
        if (currentFaultId == null) {
          setCurrentFaultId(prevFaultId + 1);
          setPostFaultDataCount(0);
        } else {
          setPostFaultDataCount((count) => count + 1);
          if (postFaultDataCount === postFaultThreshold) {
            setPause.open();
            const topKKeys = getTopKElements(dataPoints,topkfeatures);
            console.log(topKKeys);
            const filteredObject = topKKeys.reduce(
              (acc: Record<string, number[]>, key) => {
                acc[key] = dataPoints[key].map((a) => Number(a));
                return acc;
              },
              {}
            );
            const filePath = fileId2fileName[selectedFileId]; // Get the file path
            sendFaultToBackend(filteredObject, `Fault-${currentFaultId}`, filePath);
          }
        }
      } else {
        if (currentFaultId !== null) {
          setPrevFaultId(currentFaultId);
          setCurrentFaultId(null);
          setPostFaultDataCount(0);
        }
      }
    }
  }, [currentRow]);

  return (
    <div>
      <div id="simulator">
        <Simulator
          csvFile={fileId2fileName[selectedFileId]}
          interval={1000 / interval}
          setCurrentRow={setCurrentRow}
          pause={pause}
        />
      </div>
      <div>
        <AppShell
          header={{ height: 60 }}
          navbar={{
            width: 200,
            breakpoint: "sm",
            collapsed: { mobile: !opened },
          }}
          padding="md"
        >
          <AppShell.Header>
            <Group align="center" gap="xs" h="100%" pl="md" wrap="nowrap">
              <Burger
                opened={opened}
                onClick={toggle}
                hiddenFrom="sm"
                size="sm"
              />
              <Text fw={700} size="xl">
                FaultExplainer
              </Text>
              <Group h="100%" w="200%" justify="center" wrap="nowrap">
                <label htmlFor="fileSelect">Fault:</label>
                <Select
                  id="fileSelect"
                  inputSize="sm"
                  value={fault_name[selectedFileId]}
                  onChange={handleFileChange}
                  data={fault_name}
                  allowDeselect={false}
                />
                <ActionIcon
                  variant="subtle"
                  aria-label="Settings"
                  onClick={() => setPause.toggle()}
                >
                  {pause ? (
                    <IconPlayerPlayFilled stroke={1.5} />
                  ) : (
                    <IconPlayerPauseFilled stroke={1.5} />
                  )}
                </ActionIcon>
                <Slider
                  min={0}
                  max={20}
                  step={0.0005}
                  value={sliderValue}
                  onChange={setSliderValue}
                  onChangeEnd={setInterval}
                  defaultValue={1}
                  miw="100px"
                />
              </Group>
            </Group>
          </AppShell.Header>

          <AppShell.Navbar>
            <Box>
              <NavLink
                autoContrast
                key={"plot"}
                leftSection={<IconChartHistogram size="1.5rem" />}
                label={<Text size="lg">Monitoring</Text>}
                component={Link}
                to={"/plot"}
                variant="filled"
                active={location.pathname === "/plot"}
              />
              <NavLink
                autoContrast
                key={"chat"}
                leftSection={<IconRobot size="1.5rem" />}
                label={<Text size="lg">Assistant</Text>}
                component={Link}
                to={"/"}
                variant="filled"
                active={location.pathname === "/"}
              />
              <NavLink
                autoContrast
                key={"history"}
                leftSection={<IconReport size="1.5rem" />}
                label={<Text size="lg">Fault History</Text>}
                component={Link}
                to={"/history"}
                variant="filled"
                active={location.pathname === "/history"}
              />
            </Box>
          </AppShell.Navbar>

          <AppShell.Main>
            <StatContext.Provider value={t2_stat}>
              <ConservationContext.Provider
                value={{ conversation, setConversation }}
              >
                <DataPointsContext.Provider value={dataPoints}>
                  {currentRow && <Outlet />}
                </DataPointsContext.Provider>
              </ConservationContext.Provider>
            </StatContext.Provider>
          </AppShell.Main>
        </AppShell>
      </div>
    </div>
  );
}

// eslint-disable-next-line react-refresh/only-export-components
export function useDataPoints() {
  return useContext(DataPointsContext);
}

// eslint-disable-next-line react-refresh/only-export-components
export function useConversationState() {
  return useContext(ConservationContext);
}

// eslint-disable-next-line react-refresh/only-export-components
export function useStatState() {
  return useContext(StatContext);
}
