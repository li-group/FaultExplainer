// import React from 'react'
import ReactDOM from "react-dom/client";
import "@mantine/core/styles.css";
import { MantineProvider } from "@mantine/core";
import App from "./App.tsx";
import QuestionsPage from "./pages/ChatPage.tsx";
import HistoryPage from "./pages/FaultReports.tsx";
import DataPage from "./pages/PlotPage.tsx";
import ErrorPage from "./error-page.tsx";
import { createBrowserRouter, RouterProvider } from "react-router-dom";

const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    errorElement: <ErrorPage />,
    children: [
      {
        path: "plot",
        element: <DataPage />,
      },
      {
        // path: "chat",
        index: true,
        element: <QuestionsPage />,
      },
      {
        path: "history",
        element: <HistoryPage />,
      },
    ],
  },
]);

ReactDOM.createRoot(document.getElementById("root")!).render(
  // <React.StrictMode>
  <MantineProvider defaultColorScheme="dark">
    <RouterProvider router={router} />
  </MantineProvider>
  // </React.StrictMode>,
);
