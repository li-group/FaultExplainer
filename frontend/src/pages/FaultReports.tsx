import { useStatState, useConversationState } from "../App";
import {
  ScrollArea,
  Text,
  Accordion,
  Space,
  Card,
  Image,
  SimpleGrid,
} from "@mantine/core";
import { marked } from "marked";
import { AreaChart } from "@mantine/charts";

export default function HistoryPage() {
  const conversation = useConversationState().conversation;
  const t2_stat = useStatState();
  const transformedData = t2_stat.map((item) => ({
    ...item,
    anomaly: item.anomaly ? item.t2_stat : 0,
  }));
  return (
    <ScrollArea h={`calc(100vh - 60px - 32px)`}>
      <Text
        size="xl"
        ta="center"
        dangerouslySetInnerHTML={{ __html: "T<sup>2</sup> Statistic" }}
      />

      <AreaChart
        h={300}
        data={transformedData}
        dataKey="time"
        series={[
          { name: "t2_stat", label: "T-squred stat", color: "green.2" },
          { name: "anomaly", label: "Anomaly", color: "red.4" },
        ]}
        curveType="step"
        tickLine="x"
        withDots={false}
        withGradient={false}
        fillOpacity={0.75}
        strokeWidth={0}
        withYAxis={false}
      />

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
