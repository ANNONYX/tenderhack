import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { steApi } from '../services/steApi';
import { STEResponse } from '../types';
import { LoadingSpinner } from '../components/Common/LoadingSpinner';
import { ErrorMessage } from '../components/Common/ErrorMessage';
import { ImageWithFallback } from '../components/figma/ImageWithFallback';
import { ArrowLeft, Package } from 'lucide-react';

export function STEDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [ste, setSte] = useState<STEResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadSTE = async () => {
      if (!id) return;
      
      setLoading(true);
      setError(null);
      try {
        const data = await steApi.getSTEById(parseInt(id));
        setSte(data);
      } catch (err) {
        setError('Не удалось загрузить детали СТЕ');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    loadSTE();
  }, [id]);

  if (loading) return <LoadingSpinner text="Загрузка деталей СТЕ..." />;
  if (error) return <ErrorMessage message={error} onRetry={() => window.location.reload()} />;
  if (!ste) return <ErrorMessage message="СТЕ не найдена" />;

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <button
          onClick={() => navigate(-1)}
          className="flex items-center space-x-2 text-gray-600 hover:text-[rgb(219,43,33)] mb-6 transition-colors"
        >
          <ArrowLeft size={20} />
          <span>Назад</span>
        </button>

        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          <div className="grid md:grid-cols-2 gap-8 p-8">
            <div>
              <div className="aspect-square bg-gray-100 rounded-lg flex items-center justify-center overflow-hidden">
                {ste.image_url ? (
                  <ImageWithFallback
                    src={ste.image_url}
                    alt={ste.name}
                    className="w-full h-full object-contain"
                  />
                ) : (
                  <Package size={120} className="text-gray-300" />
                )}
              </div>
            </div>

            <div>
              <h1 className="text-2xl text-gray-900 mb-6">{ste.name}</h1>

              <div className="space-y-4">
                <div className="border-b border-gray-100 pb-4">
                  <h2 className="text-sm text-gray-500 mb-3">Общая информация</h2>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-gray-600">ID СТЕ:</span>
                      <span className="text-gray-900">{ste.ste_id}</span>
                    </div>
                    {ste.manufacturer && (
                      <div className="flex justify-between">
                        <span className="text-gray-600">Производитель:</span>
                        <span className="text-gray-900">{ste.manufacturer}</span>
                      </div>
                    )}
                    {ste.model && (
                      <div className="flex justify-between">
                        <span className="text-gray-600">Модель:</span>
                        <span className="text-gray-900">{ste.model}</span>
                      </div>
                    )}
                    {ste.country && (
                      <div className="flex justify-between">
                        <span className="text-gray-600">Страна:</span>
                        <span className="text-gray-900">{ste.country}</span>
                      </div>
                    )}
                  </div>
                </div>

                <div className="border-b border-gray-100 pb-4">
                  <h2 className="text-sm text-gray-500 mb-3">Категория</h2>
                  <div className="bg-gray-50 rounded-lg p-3">
                    <div className="text-sm text-gray-900">{ste.category_name}</div>
                    <div className="text-xs text-gray-500 mt-1">ID: {ste.category_id}</div>
                  </div>
                </div>

                <div>
                  <h2 className="text-sm text-gray-500 mb-3">Характеристики</h2>
                  {Object.keys(ste.characteristics).length > 0 ? (
                    <div className="bg-gray-50 rounded-lg p-4 space-y-2">
                      {Object.entries(ste.characteristics).map(([key, value]) => (
                        <div key={key} className="flex justify-between border-b border-gray-200 last:border-0 pb-2 last:pb-0">
                          <span className="text-gray-600">{key}:</span>
                          <span className="text-gray-900">{value || 'Не указано'}</span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="bg-gray-50 rounded-lg p-4 text-center text-gray-500">
                      Характеристики отсутствуют
                    </div>
                  )}
                </div>
              </div>

              <div className="mt-8 flex space-x-4">
                <button
                  onClick={() => navigate('/')}
                  className="flex-1 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Вернуться к поиску
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
