import { useState, useEffect } from 'react';
import { Search, X } from 'lucide-react';

interface STESearchProps {
  onSearch: (query: string) => void;
  initialValue?: string;
}

export function STESearch({ onSearch, initialValue = '' }: STESearchProps) {
  const [query, setQuery] = useState(initialValue);

  useEffect(() => {
    const debounceTimer = setTimeout(() => {
      onSearch(query);
    }, 500);

    return () => clearTimeout(debounceTimer);
  }, [query, onSearch]);

  return (
    <div className="relative">
      <div className="flex items-center">
        <div className="relative flex-1">
          <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Поиск СТЕ по названию, производителю, модели..."
            className="w-full pl-12 pr-12 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[rgb(219,43,33)] focus:border-transparent"
          />
          {query && (
            <button
              onClick={() => setQuery('')}
              className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
            >
              <X size={20} />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
