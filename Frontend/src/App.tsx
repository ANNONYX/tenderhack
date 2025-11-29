import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Header } from './components/Layout/Header';
import { HomePage } from './pages/HomePage';
import { STEDetailPage } from './pages/STEDetailPage';
import { AggregationsPage } from './pages/AggregationsPage';
import { AggregationDetailPage } from './pages/AggregationDetailPage';

export default function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Header />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/ste/:id" element={<STEDetailPage />} />
          <Route path="/aggregations" element={<AggregationsPage />} />
          <Route path="/aggregations/:id" element={<AggregationDetailPage />} />
        </Routes>
      </div>
    </Router>
  );
}
