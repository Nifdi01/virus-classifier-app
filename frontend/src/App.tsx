import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Processor from "./pages/Processor";
import "./index.css";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";

export default function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/processor" element={<Processor />} />
      </Routes>
      <Footer />
    </BrowserRouter>
  );
}
