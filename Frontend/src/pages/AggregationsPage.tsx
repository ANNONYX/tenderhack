import { useState, useEffect } from 'react';
import { aggregationApi } from '../services/aggregationApi';
import { AggregationResponse } from '../types';
import { AggregationCard } from '../components/Aggregation/AggregationCard';
import { LoadingSpinner } from '../components/Common/LoadingSpinner';
import { ErrorMessage } from '../components/Common/ErrorMessage';
import { HelpModal } from '../components/Common/HelpModal';
import { Grid3x3, Sparkles, HelpCircle } from 'lucide-react';

export function AggregationsPage() {
  const [aggregations, setAggregations] = useState<AggregationResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [savedOnly, setSavedOnly] = useState(false);
  const [groupingAll, setGroupingAll] = useState(false);
  const [showHelp, setShowHelp] = useState(false);

  const loadAggregations = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await aggregationApi.getAggregations({
        saved_only: savedOnly,
        limit: 100,
      });
      setAggregations(data);
    } catch (err) {
      setError('Не удалось загрузить агрегации');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAggregations();
  }, [savedOnly]);

  const handleDelete = async (id: number) => {
    if (!window.confirm('Вы уверены, что хотите удалить эту агрегацию?')) {
      return;
    }

    try {
      await aggregationApi.deleteAggregation(id);
      setAggregations((prev) => prev.filter((a) => a.id !== id));
    } catch (err) {
      alert('Не удалось удалить агрегацию');
      console.error(err);
    }
  };

  const handleSave = async (id: number) => {
    try {
      await aggregationApi.saveAggregation(id);
      setAggregations((prev) =>
        prev.map((a) => (a.id === id ? { ...a, is_saved: true } : a))
      );
    } catch (err) {
      alert('Не удалось сохранить агрегацию');
      console.error(err);
    }
  };

  const handleGroupAll = async () => {
    setGroupingAll(true);
    try {
      const result = await aggregationApi.performGrouping({
        force_regenerate: true,
      });
      setAggregations(result.aggregations);
    } catch (err) {
      setError('Не удалось выполнить группировку');
      console.error(err);
    } finally {
      setGroupingAll(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <HelpModal isOpen={showHelp} onClose={() => setShowHelp(false)} />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8 flex items-start justify-between">
          <div>
            <h1 className="text-3xl text-gray-900 mb-2">Агрегации СТЕ</h1>
            <p className="text-gray-600">
              Управление группировками стандартных товарных единиц
            </p>
          </div>
          
          <button
            onClick={() => setShowHelp(true)}
            className="px-4 py-2 bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100 transition-colors flex items-center space-x-2 border border-blue-200"
          >
            <HelpCircle size={20} />
            <span>Справка для модератора</span>
          </button>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={savedOnly}
                  onChange={(e) => setSavedOnly(e.target.checked)}
                  className="w-4 h-4 text-[rgb(219,43,33)] border-gray-300 rounded focus:ring-[rgb(219,43,33)]"
                />
                <span className="text-gray-700">Показать только сохраненные</span>
              </label>
            </div>

            <button
              onClick={handleGroupAll}
              disabled={groupingAll}
              className="px-6 py-3 bg-[rgb(219,43,33)] text-white rounded-lg hover:bg-[rgb(199,23,13)] transition-colors flex items-center space-x-2 disabled:opacity-50"
            >
              <Sparkles size={20} />
              <span>{groupingAll ? 'Группировка...' : 'Сгруппировать все СТЕ'}</span>
            </button>
          </div>
        </div>

        {error && <ErrorMessage message={error} onRetry={loadAggregations} />}

        {loading && <LoadingSpinner text="Загрузка агрегаций..." />}

        {!loading && !error && aggregations.length === 0 && (
          <div className="text-center py-12">
            <Grid3x3 size={64} className="mx-auto text-gray-300 mb-4" />
            <h3 className="text-xl text-gray-900 mb-2">Агрегации не найдены</h3>
            <p className="text-gray-600 mb-6">
              {savedOnly
                ? 'У вас пока нет сохраненных агрегаций'
                : 'Выполните группировку СТЕ для создания агрегаций'}
            </p>
            <button
              onClick={handleGroupAll}
              className="px-6 py-3 bg-[rgb(219,43,33)] text-white rounded-lg hover:bg-[rgb(199,23,13)] transition-colors inline-flex items-center space-x-2"
            >
              <Sparkles size={20} />
              <span>Создать агрегации</span>
            </button>
          </div>
        )}

        {!loading && !error && aggregations.length > 0 && (
          <>
            <div className="mb-6">
              <p className="text-gray-600">
                Найдено: <span className="text-gray-900">{aggregations.length}</span> агрегаций
              </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {aggregations.map((aggregation) => (
                <AggregationCard
                  key={aggregation.id}
                  aggregation={aggregation}
                  onDelete={handleDelete}
                  onSave={handleSave}
                />
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
