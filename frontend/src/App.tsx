import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Layout } from "./components/Layout";
import { DashboardPage } from "./pages/DashboardPage";
import { CrawlPage } from "./pages/CrawlPage";
import { ArticlePage } from "./pages/ArticlePage";

const queryClient = new QueryClient({
  defaultOptions: { queries: { staleTime: 3000, retry: 1 } },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/crawl" element={<CrawlPage />} />
            <Route path="/crawl/:jobId" element={<CrawlPage />} />
            <Route path="/articles" element={<ArticlePage />} />
            <Route path="/articles/:id" element={<ArticlePage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
