import {
  StatContextId,
  useStatState,
  useConversationState,
  startTime,
} from "../App";
import {
  ScrollArea,
  Text,
  Accordion,
  Space,
  Card,
  Image,
  SimpleGrid,
} from "@mantine/core";
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
import { marked } from "marked";

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

export default function HistoryPage() {
  const conversation = useConversationState().conversation;
  const t2_stat = useStatState();
  return (
    <ScrollArea h={`calc(100vh - 60px - 32px)`}>
      <Text
        size="xl"
        ta="center"
        dangerouslySetInnerHTML={{ __html: "T<sup>2</sup> Statistic" }}
      />
      <div
        className="chart-wrapper"
        key={"t2_stat"}
        style={{
          background: "#f0f0f0",
          padding: "10px",
          borderRadius: "5px",
        }}
      >
        <LineChart data={t2_stat} />
      </div>
      <Space h="xl" />
      <Accordion variant="separated">
        {conversation.map(
          (msg) =>
            msg.explanation && (
              <Accordion.Item key={msg.id} value={`Fault ${msg.id}`}>
                <Accordion.Control>{msg.id}</Accordion.Control>
                <Accordion.Panel>
                  <Card shadow="sm" padding="lg" radius="md" withBorder>
                    {msg.images && (
                      <Card.Section>
                        <SimpleGrid cols={Math.min(msg.images.length, 3)}>
                          {(() => {
                            return msg.images.map((img, idx) => (
                              <Image
                                key={idx}
                                src={`data:image/png;base64,${img.image}`}
                                alt={`Graph for ${img.name}`}
                                radius="md"
                              />
                            ));
                          })()}
                        </SimpleGrid>
                      </Card.Section>
                    )}
                    {msg.text && (
                      <div
                        dangerouslySetInnerHTML={{
                          __html: marked.parse(msg.text),
                        }}
                      />
                    )}
                  </Card>
                </Accordion.Panel>
                {/* {idx}:{msg.explanation.toString()} */}
              </Accordion.Item>
            )
        )}
      </Accordion>
    </ScrollArea>
  );
}

const LineChart = ({ data }: { data: StatContextId[] }) => {
  const chartData = {
    labels: Array.from({ length: data.length }, (_, i) => {
      const currentTime = new Date(startTime);
      currentTime.setMinutes(currentTime.getMinutes() + i * 3);
      return currentTime.toISOString();
    }),
    datasets: [
      {
        label: "",
        data: data.map((x) => x.t2_stat),
        fill: "start",
        borderColor: "rgb(75, 192, 192)",
        stepped: true,
        pointRadius: 0.5,
        borderWidth: 1,
        pointHoverRadius: 0,
      },
      {
        label: "",
        data: data.map((x) => (x.anomaly ? x.t2_stat : 0)),
        fill: "start",
        borderColor: "rgb(75, 192, 192)",
        backgroundColor: "rgba(250, 0, 0, 0.4)",
        stepped: true,
        pointRadius: 0,
        borderWidth: 0,
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
    },
  };

  return <Line height="100%" data={chartData} options={chartOptions} />;
};
