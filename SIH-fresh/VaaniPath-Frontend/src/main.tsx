import { createRoot } from "react-dom/client";
import App from "./App.tsx";
import "./index.css";
import "./i18n";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            staleTime: 1000 * 60 * 10, // 10 minutes (increased from 5)
            refetchOnWindowFocus: false, // Don't refetch on window focus
            refetchOnMount: false, // Don't refetch on component mount if data exists
            retry: 1,
        },
    },
});

createRoot(document.getElementById("root")!).render(
    <QueryClientProvider client={queryClient}>
        <App />
    </QueryClientProvider>
);
