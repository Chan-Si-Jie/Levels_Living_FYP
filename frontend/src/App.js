import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import LoginPage from "./components/index";
import Deliveries from "./components/deliveries";
import Details from "./components/details";
import OrderScheduling from "./components/OrderScheduling";
import ScheduledDeliveries from "./components/ScheduledDeliveries";
import DriverDashboard from "./components/DriverDashboard";
import HQDashboard from "./components/HQDashboard";
function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route path="/deliveries" element={<Deliveries />} />
        <Route path="/details" element={<Details />} />
        <Route path="/schedule-orders" element={<OrderScheduling />} />
        <Route path="/scheduled-deliveries" element={<ScheduledDeliveries />} />
        <Route path="/driver-dashboard" element={<DriverDashboard />} />
        <Route path="/hq-dashboard" element={<HQDashboard />} />
      </Routes>
    </Router>
  );
}

export default App;

