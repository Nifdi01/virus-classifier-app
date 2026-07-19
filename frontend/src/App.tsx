import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import Home from "./pages/Home";
import Processor from "./pages/Processor";
import History from "./pages/History";
import JobDetail from "./pages/JobDetail";

export default function App() {
  return (
    <BrowserRouter>
      {/* 1. Main layout container spanning full viewport height */}
      <div className="flex flex-col min-h-screen">
        <Navbar />

        {/* 2. Wrapper that expands to push the footer down */}
        <main className="grow">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/processor" element={<Processor />} />
            <Route path="/history" element={<History />} />
            <Route path="/history/:jobId" element={<JobDetail />} />
          </Routes>
        </main>

        <Footer />
      </div>
    </BrowserRouter>
  );
}
