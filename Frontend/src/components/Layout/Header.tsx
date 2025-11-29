import { Link, useLocation } from 'react-router-dom';
import { Search, Home, Grid3x3 } from 'lucide-react';

export function Header() {
  const location = useLocation();

  const isActive = (path: string) => {
    return location.pathname === path;
  };

  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-[rgb(219,43,33)] flex items-center justify-center">
              <span className="text-white">П</span>
            </div>
            <div>
              <div className="text-gray-900">ПОРТАЛ ПОСТАВЩИКОВ</div>
              <div className="text-xs text-gray-500">Сервис группировки СТЕ</div>
            </div>
          </Link>

          <nav className="flex space-x-8">
            <Link
              to="/"
              className={`flex items-center space-x-2 px-3 py-2 transition-colors ${
                isActive('/')
                  ? 'text-[rgb(219,43,33)] border-b-2 border-[rgb(219,43,33)]'
                  : 'text-gray-600 hover:text-[rgb(219,43,33)]'
              }`}
            >
              <Home size={18} />
              <span>Поиск СТЕ</span>
            </Link>
            <Link
              to="/aggregations"
              className={`flex items-center space-x-2 px-3 py-2 transition-colors ${
                isActive('/aggregations')
                  ? 'text-[rgb(219,43,33)] border-b-2 border-[rgb(219,43,33)]'
                  : 'text-gray-600 hover:text-[rgb(219,43,33)]'
              }`}
            >
              <Grid3x3 size={18} />
              <span>Агрегации</span>
            </Link>
          </nav>
        </div>
      </div>
    </header>
  );
}
