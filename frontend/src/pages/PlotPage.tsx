import { useDataPoints, columnFilter, DataPointsId, startTime } from "../App";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  TimeScale,
  ChartOptions,
} from "chart.js";
import "chartjs-adapter-date-fns";
import { ScrollArea, SimpleGrid } from "@mantine/core";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  TimeScale
);

export default function DataPage() {
  const fullDataPoints = useDataPoints();
  const dataPoints = Object.keys(fullDataPoints)
    .filter((key) => columnFilter.includes(key))
    .reduce((obj: DataPointsId, key) => {
      obj[key] = fullDataPoints[key];
      return obj;
    }, {});

  if (!dataPoints) {
    return <div>Loading...</div>;
  }

  // const timeLabels = fullDataPoints["time"].map((time) =>
  //   new Date(time).toLocaleTimeString()
  // );
  console.log(fullDataPoints);
  return (
    <ScrollArea h={`calc(100vh - 60px - 32px)`}>
      <SimpleGrid cols={3}>
        {Object.entries(dataPoints).map(([fieldName, values]) => (
          <div
            className="chart-wrapper"
            key={fieldName}
            style={{
              background: "#f0f0f0",
              padding: "0px",
              borderRadius: "5px",
              height: "220px",
            }}
          >
            <LineChart
              data={values}
              fieldName={fieldName}
              labels={fullDataPoints["time"]}
            />
          </div>
        ))}
      </SimpleGrid>
    </ScrollArea>
  );
}

const LineChart = ({
  data,
  fieldName,
  labels,
}: {
  data: number[];
  fieldName: string;
  labels: number[];
}) => {
  console.log(labels);
  const chartData = {
    labels: labels.map((interval) => {
      const currentTime = new Date(startTime);
      currentTime.setMinutes(currentTime.getMinutes() + interval * 20 * 3);
      return currentTime.toISOString();
    }),
    datasets: [
      {
        label: "",
        data: data,
        fill: true,
        borderColor: "rgb(75, 192, 192)",
        stepped: true,
        pointRadius: 0.5,
        borderWidth: 1,
        pointHoverRadius: 0,
      },
    ],
  };

  const chartOptions: ChartOptions<"line"> = {
    responsive: true,
    animation: {
      duration: 0.25,
    },
    scales: {
      x: {
        type: "time",
        time: {
          // unit: "minute",
          tooltipFormat: "PPpp", // Tooltip format for time
          displayFormats: {
            minute: "HH:mm", // Display format for the x-axis labels
          },
        },
        title: {
          display: true,
          text: "Time",
        },
      },
      y: {
        title: {
          display: false,
          text: "Values",
        },
      },
    },
    plugins: {
      legend: {
        display: false,
      },
      title: {
        display: true,
        text: fieldName,
      },
    },
  };

  return (
    <Line style={{ height: "100%" }} data={chartData} options={chartOptions} />
  );
};
