import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Processor from "./pages/Processor";
import "./index.css";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/processor" element={<Processor />} />
      </Routes>
    </BrowserRouter>
  );
}
