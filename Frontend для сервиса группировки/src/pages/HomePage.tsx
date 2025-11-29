import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { STESearch } from '../components/STE/STESearch';
import { STECard } from '../components/STE/STECard';
import { LoadingSpinner } from '../components/Common/LoadingSpinner';
import { ErrorMessage } from '../components/Common/ErrorMessage';
import { Pagination } from '../components/Common/Pagination';
import { steApi } from '../services/steApi';
import { aggregationApi } from '../services/aggregationApi';
import { STEResponse } from '../types';
import { Grid3x3, Sparkles } from 'lucide-react';

export function HomePage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [steList, setSteList] = useState<STEResponse[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedSTEs, setSelectedSTEs] = useState<Set<number>>(new Set());
  const [grouping, setGrouping] = useState(false);
  const itemsPerPage = 20;
  const navigate = useNavigate();

  const loadSTEs = useCallback(async (query: string, page: number) => {
    setLoading(true);
    setError(null);
    try {
      const offset = (page - 1) * itemsPerPage;
      const data = await steApi.searchSTE({
        query: query || undefined,
        limit: itemsPerPage,
        offset,
      });
      setSteList(data.items);
      setTotal(data.total);
    } catch (err) {
      setError('Не удалось загрузить СТЕ. Проверьте подключение к серверу.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleSearch = useCallback((query: string) => {
    setSearchQuery(query);
    setCurrentPage(1);
    loadSTEs(query, 1);
  }, [loadSTEs]);

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    loadSTEs(searchQuery, page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleSelectSTE = (id: number) => {
    setSelectedSTEs((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(id)) {
        newSet.delete(id);
      } else {
        newSet.add(id);
      }
      return newSet;
    });
  };

  const handleGroupSelected = async () => {
    if (selectedSTEs.size === 0) {
      alert('Выберите хотя бы одну СТЕ для группировки');
      return;
    }

    setGrouping(true);
    try {
      await aggregationApi.performGrouping({
        ste_ids: Array.from(selectedSTEs),
        force_regenerate: false,
      });
      navigate('/aggregations');
    } catch (err) {
      setError('Не удалось выполнить группировку');
      console.error(err);
    } finally {
      setGrouping(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl text-gray-900 mb-2">Поиск стандартных товарных единиц</h1>
          <p className="text-gray-600">
            Найдите СТЕ по названию, производителю или модели
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <STESearch onSearch={handleSearch} />
        </div>

        {selectedSTEs.size > 0 && (
          <div className="bg-white rounded-lg shadow-sm p-4 mb-8 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-[rgb(219,43,33)] rounded-full flex items-center justify-center text-white">
                {selectedSTEs.size}
              </div>
              <div>
                <div className="text-gray-900">Выбрано СТЕ: {selectedSTEs.size}</div>
                <div className="text-sm text-gray-500">Готово к группировке</div>
              </div>
            </div>
            <button
              onClick={handleGroupSelected}
              disabled={grouping}
              className="px-6 py-3 bg-[rgb(219,43,33)] text-white rounded-lg hover:bg-[rgb(199,23,13)] transition-colors flex items-center space-x-2 disabled:opacity-50"
            >
              <Sparkles size={20} />
              <span>{grouping ? 'Группировка...' : 'Сгруппировать выбранные'}</span>
            </button>
          </div>
        )}

        {error && <ErrorMessage message={error} onRetry={() => loadSTEs(searchQuery, currentPage)} />}

        {loading && <LoadingSpinner text="Загрузка СТЕ..." />}

        {!loading && !error && steList.length === 0 && (
          <div className="text-center py-12">
            <Grid3x3 size={64} className="mx-auto text-gray-300 mb-4" />
            <h3 className="text-xl text-gray-900 mb-2">СТЕ не найдены</h3>
            <p className="text-gray-600">
              {searchQuery
                ? 'Попробуйте изменить параметры поиска'
                : 'Начните поиск, чтобы увидеть результаты'}
            </p>
          </div>
        )}

        {!loading && !error && steList.length > 0 && (
          <>
            <div className="mb-6">
              <p className="text-gray-600">
                Найдено: <span className="text-gray-900">{total}</span> СТЕ
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {steList.map((ste) => (
                <STECard
                  key={ste.id}
                  ste={ste}
                  isSelected={selectedSTEs.has(ste.id)}
                  onSelect={handleSelectSTE}
                  showCheckbox
                />
              ))}
            </div>

            <Pagination
              currentPage={currentPage}
              totalItems={total}
              itemsPerPage={itemsPerPage}
              onPageChange={handlePageChange}
            />
          </>
        )}
      </div>
    </div>
  );
}
