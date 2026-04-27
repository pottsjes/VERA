import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import Browse from './pages/Browse';
import Upload from './pages/Upload';
import Recommend from './pages/Recommend';

const navClass = ({ isActive }: { isActive: boolean }) =>
  `px-3 py-2 rounded ${isActive ? 'bg-gray-800 text-white' : 'text-gray-300 hover:text-white'}`;

export default function App() {
  return (
    <BrowserRouter>
      <nav className="bg-gray-900 px-6 py-3 flex items-center gap-6">
        <span className="text-white font-bold text-lg">V.E.R.A.</span>
        <NavLink to="/" className={navClass}>Wardrobe</NavLink>
        <NavLink to="/upload" className={navClass}>Upload</NavLink>
        <NavLink to="/recommend" className={navClass}>Recommend</NavLink>
      </nav>

      <main className="max-w-6xl mx-auto px-4 py-8">
        <Routes>
          <Route path="/" element={<Browse />} />
          <Route path="/upload" element={<Upload />} />
          <Route path="/recommend" element={<Recommend />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}
