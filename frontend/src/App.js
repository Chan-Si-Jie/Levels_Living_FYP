import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import LoginPage from "./components/index";
import Deliveries from "./components/deliveries";
import Details from "./components/details";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route path="/deliveries" element={<Deliveries />} />
        <Route path="/details" element={<Details />} />
      </Routes>
    </Router>
  );
}

export default App;

