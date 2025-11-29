import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { aggregationApi } from '../services/aggregationApi';
import { ratingApi } from '../services/ratingApi';
import { AggregationResponse, AggregationRatingsResponse } from '../types';
import { LoadingSpinner } from '../components/Common/LoadingSpinner';
import { ErrorMessage } from '../components/Common/ErrorMessage';
import { RatingStars } from '../components/Rating/RatingStars';
import { ImageWithFallback } from '../components/figma/ImageWithFallback';
import { ArrowLeft, Bookmark, Trash2, Package, ChevronUp, ChevronDown, Star } from 'lucide-react';

export function AggregationDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [aggregation, setAggregation] = useState<AggregationResponse | null>(null);
  const [ratings, setRatings] = useState<AggregationRatingsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [newRating, setNewRating] = useState(0);
  const [comment, setComment] = useState('');
  const [submittingRating, setSubmittingRating] = useState(false);

  const loadData = async () => {
    if (!id) return;

    setLoading(true);
    setError(null);
    try {
      const [aggData, ratingsData] = await Promise.all([
        aggregationApi.getAggregationById(parseInt(id)),
        ratingApi.getRatings(parseInt(id)).catch(() => null),
      ]);
      setAggregation(aggData);
      setRatings(ratingsData);
    } catch (err) {
      setError('Не удалось загрузить детали агрегации');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [id]);

  const handleSave = async () => {
    if (!id) return;
    try {
      await aggregationApi.saveAggregation(parseInt(id));
      setAggregation((prev) => (prev ? { ...prev, is_saved: true } : null));
    } catch (err) {
      alert('Не удалось сохранить агрегацию');
      console.error(err);
    }
  };

  const handleDelete = async () => {
    if (!id) return;
    if (!window.confirm('Вы уверены, что хотите удалить эту агрегацию?')) {
      return;
    }

    try {
      await aggregationApi.deleteAggregation(parseInt(id));
      navigate('/aggregations');
    } catch (err) {
      alert('Не удалось удалить агрегацию');
      console.error(err);
    }
  };

  const handleRemoveItem = async (itemId: number) => {
    if (!id) return;
    if (!window.confirm('Удалить эту СТЕ из группы?')) {
      return;
    }

    try {
      await aggregationApi.removeSTEFromAggregation(parseInt(id), itemId);
      setAggregation((prev) =>
        prev
          ? {
              ...prev,
              items: prev.items.filter((item) => item.id !== itemId),
              items_count: prev.items_count - 1,
            }
          : null
      );
    } catch (err) {
      alert('Не удалось удалить СТЕ');
      console.error(err);
    }
  };

  const handleMoveItem = async (itemId: number, currentOrder: number, direction: 'up' | 'down') => {
    if (!id || !aggregation) return;

    const newOrder = direction === 'up' ? currentOrder - 1 : currentOrder + 1;
    
    try {
      await aggregationApi.changeSTEOrder(parseInt(id), itemId, newOrder);
      loadData();
    } catch (err) {
      alert('Не удалось изменить порядок');
      console.error(err);
    }
  };

  const handleSubmitRating = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!id || newRating === 0) return;

    setSubmittingRating(true);
    try {
      await ratingApi.submitRating(parseInt(id), {
        rating: newRating,
        comment: comment || undefined,
      });
      setNewRating(0);
      setComment('');
      const ratingsData = await ratingApi.getRatings(parseInt(id));
      setRatings(ratingsData);
      setAggregation((prev) => (prev ? { ...prev, rating: ratingsData.average_rating } : null));
    } catch (err) {
      alert('Не удалось отправить оценку');
      console.error(err);
    } finally {
      setSubmittingRating(false);
    }
  };

  if (loading) return <LoadingSpinner text="Загрузка агрегации..." />;
  if (error) return <ErrorMessage message={error} onRetry={loadData} />;
  if (!aggregation) return <ErrorMessage message="Агрегация не найдена" />;

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <button
          onClick={() => navigate('/aggregations')}
          className="flex items-center space-x-2 text-gray-600 hover:text-[rgb(219,43,33)] mb-6 transition-colors"
        >
          <ArrowLeft size={20} />
          <span>Назад к агрегациям</span>
        </button>

        <div className="bg-white rounded-lg shadow-sm p-8 mb-6">
          <div className="flex items-start justify-between mb-6">
            <div className="flex-1">
              <h1 className="text-2xl text-gray-900 mb-4">{aggregation.name}</h1>
              
              <div className="flex items-center space-x-2 mb-4">
                <span
                  className={`px-3 py-1 rounded-full text-sm ${
                    aggregation.status === 'auto'
                      ? 'bg-blue-100 text-blue-700'
                      : 'bg-green-100 text-green-700'
                  }`}
                >
                  {aggregation.status === 'auto' ? 'Автоматическая' : 'Ручная'}
                </span>
                {aggregation.is_saved && (
                  <span className="px-3 py-1 rounded-full text-sm bg-green-100 text-green-700 flex items-center space-x-1">
                    <Bookmark size={14} />
                    <span>Сохранена</span>
                  </span>
                )}
              </div>

              {aggregation.rating && (
                <div className="mb-4">
                  <RatingStars rating={aggregation.rating} size={24} />
                </div>
              )}
            </div>

            <div className="flex items-center space-x-2">
              {!aggregation.is_saved && (
                <button
                  onClick={handleSave}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center space-x-2"
                >
                  <Bookmark size={18} />
                  <span>Сохранить</span>
                </button>
              )}
              <button
                onClick={handleDelete}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors flex items-center space-x-2"
              >
                <Trash2 size={18} />
                <span>Удалить</span>
              </button>
            </div>
          </div>

          <div className="border-t border-gray-100 pt-6">
            <h2 className="text-gray-900 mb-3">Характеристики группировки</h2>
            <div className="bg-gray-50 rounded-lg p-4 space-y-2">
              {Object.entries(aggregation.grouping_characteristics).map(([key, value]) => (
                <div key={key} className="flex justify-between border-b border-gray-200 last:border-0 pb-2 last:pb-0">
                  <span className="text-gray-600">{key}:</span>
                  <span className="text-gray-900">{value || 'Не указано'}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-8 mb-6">
          <h2 className="text-xl text-gray-900 mb-6">СТЕ в агрегации ({aggregation.items_count})</h2>
          
          <div className="space-y-4">
            {aggregation.items.map((item, index) => (
              <div key={item.id} className="border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors">
                <div className="flex items-center space-x-4">
                  <div className="w-20 h-20 bg-gray-100 rounded flex items-center justify-center overflow-hidden flex-shrink-0">
                    {item.ste.image_url ? (
                      <ImageWithFallback
                        src={item.ste.image_url}
                        alt={item.ste.name}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <Package size={32} className="text-gray-400" />
                    )}
                  </div>

                  <div className="flex-1">
                    <Link to={`/ste/${item.ste.id}`}>
                      <h3 className="text-gray-900 hover:text-[rgb(219,43,33)] transition-colors mb-1">
                        {item.ste.name}
                      </h3>
                    </Link>
                    <div className="text-sm text-gray-600 space-y-1">
                      {item.ste.manufacturer && (
                        <div>Производитель: {item.ste.manufacturer}</div>
                      )}
                      {item.ste.model && (
                        <div>Модель: {item.ste.model}</div>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    <div className="flex flex-col space-y-1">
                      <button
                        onClick={() => handleMoveItem(item.id, item.order, 'up')}
                        disabled={index === 0}
                        className="p-1 text-gray-600 hover:bg-gray-100 rounded disabled:opacity-30"
                        title="Переместить вверх"
                      >
                        <ChevronUp size={20} />
                      </button>
                      <button
                        onClick={() => handleMoveItem(item.id, item.order, 'down')}
                        disabled={index === aggregation.items.length - 1}
                        className="p-1 text-gray-600 hover:bg-gray-100 rounded disabled:opacity-30"
                        title="Переместить вниз"
                      >
                        <ChevronDown size={20} />
                      </button>
                    </div>
                    <button
                      onClick={() => handleRemoveItem(item.id)}
                      className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                      title="Удалить из группы"
                    >
                      <Trash2 size={20} />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-8">
          <h2 className="text-xl text-gray-900 mb-6">Оценки</h2>

          <form onSubmit={handleSubmitRating} className="mb-8 pb-8 border-b border-gray-100">
            <div className="mb-4">
              <label className="block text-gray-700 mb-2">Ваша оценка</label>
              <RatingStars
                rating={newRating}
                interactive
                onRatingChange={setNewRating}
                size={32}
              />
            </div>

            <div className="mb-4">
              <label className="block text-gray-700 mb-2">Комментарий (опционально)</label>
              <textarea
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[rgb(219,43,33)] focus:border-transparent"
                rows={3}
                placeholder="Ваш комментарий к этой группировке..."
              />
            </div>

            <button
              type="submit"
              disabled={newRating === 0 || submittingRating}
              className="px-6 py-3 bg-[rgb(219,43,33)] text-white rounded-lg hover:bg-[rgb(199,23,13)] transition-colors disabled:opacity-50 flex items-center space-x-2"
            >
              <Star size={20} />
              <span>{submittingRating ? 'Отправка...' : 'Отправить оценку'}</span>
            </button>
          </form>

          {ratings && ratings.ratings.length > 0 && (
            <div>
              <h3 className="text-gray-900 mb-4">
                История оценок ({ratings.ratings_count})
              </h3>
              <div className="space-y-4">
                {ratings.ratings.map((rating) => (
                  <div key={rating.id} className="bg-gray-50 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <RatingStars rating={rating.rating} size={18} />
                      <span className="text-sm text-gray-500">
                        {new Date(rating.created_at).toLocaleDateString('ru-RU')}
                      </span>
                    </div>
                    {rating.comment && (
                      <p className="text-gray-700 text-sm">{rating.comment}</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {ratings && ratings.ratings.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              Пока нет оценок. Будьте первым!
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
