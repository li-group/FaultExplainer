import '@mantine/core/styles.css';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ChatPage } from './pages/ChatPage';
import { PlotPage } from './pages/PlotPage';
import { FaultReports } from './pages/FaultReports';
import { Layout } from './Layout';
import { ChatProvider } from './ChatContext';
import { PlotProvider } from './PlotContext';
import { ReportProvider } from './ReportContext';


export function App() {
  return (
    <ReportProvider>
      <PlotProvider>
        <ChatProvider>
          <Router>
            <Routes>
              <Route path="/" element={<Layout />}>
                <Route index element={<ChatPage />} />
                <Route path="plot" element={<PlotPage />} />
                <Route path="fault_reports" element={<FaultReports />} />
              </Route>
            </Routes>
          </Router>
        </ChatProvider>
      </PlotProvider>
    </ReportProvider>
  )
}
