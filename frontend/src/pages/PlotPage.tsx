import {
  useDataPoints,
  columnFilter,
  DataPointsId,
  startTime,
  columnFilterUnits,
} from "../App";
import { ScrollArea, SimpleGrid } from "@mantine/core";
import { AreaChart } from "@mantine/charts";

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

  return (
    <ScrollArea h={`calc(100vh - 60px - 32px)`}>
      <SimpleGrid type="container" cols={3}>
        {Object.entries(dataPoints).map(([fieldName, values]) => {
          // console.log(values);
          const timeAxis = fullDataPoints.time.map((item) => {
            const date = new Date(
              startTime.getTime() + (item * 3 * 60000) / 0.05
            );
            return date.getHours() + ":" + date.getMinutes();
          });

          return (
            <div key={fieldName} style={{ textAlign: "center" }}>
              <h4>{fieldName}</h4>
              <AreaChart
                h={300}
                key={fieldName}
                data={values.map((item, idx) => ({
                  data: item,
                  time: timeAxis[idx],
                }))}
                dataKey="time"
                yAxisLabel={columnFilterUnits[fieldName]}
                series={[{ name: "data", color: "indigo.6" }]}
                curveType="step"
                tickLine="x"
                withTooltip={false}
                withDots={false}
              />
            </div>
          );
        })}
      </SimpleGrid>
    </ScrollArea>
  );
}
