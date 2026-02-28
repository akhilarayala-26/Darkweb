import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { TopicSelector } from './pages/TopicSelector';
import { TopicDashboard } from './pages/TopicDashboard';
import { Admin } from './pages/Admin';

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-950 text-white">
        <Routes>
          <Route path="/" element={<TopicSelector />} />
          <Route path="/topic/:topicId" element={<TopicDashboard />} />
          <Route path="/admin" element={<Admin />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
