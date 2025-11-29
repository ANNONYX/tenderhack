import { Link } from 'react-router-dom';
import { AggregationResponse } from '../../types';
import { RatingStars } from '../Rating/RatingStars';
import { ImageWithFallback } from '../figma/ImageWithFallback';
import { Bookmark, Package, Trash2 } from 'lucide-react';

interface AggregationCardProps {
  aggregation: AggregationResponse;
  onDelete?: (id: number) => void;
  onSave?: (id: number) => void;
}

export function AggregationCard({ aggregation, onDelete, onSave }: AggregationCardProps) {
  const firstThreeItems = aggregation.items.slice(0, 3);

  return (
    <div className="bg-white rounded-lg border border-gray-200 hover:shadow-lg transition-shadow p-6">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <Link to={`/aggregations/${aggregation.id}`}>
            <h3 className="text-lg text-gray-900 hover:text-[rgb(219,43,33)] transition-colors mb-2">
              {aggregation.name}
            </h3>
          </Link>
          
          <div className="flex items-center space-x-2 mb-3">
            <span
              className={`px-3 py-1 rounded-full text-xs ${
                aggregation.status === 'auto'
                  ? 'bg-blue-100 text-blue-700'
                  : 'bg-green-100 text-green-700'
              }`}
            >
              {aggregation.status === 'auto' ? 'Автоматическая' : 'Ручная'}
            </span>
            {aggregation.is_saved && (
              <span className="px-3 py-1 rounded-full text-xs bg-green-100 text-green-700 flex items-center space-x-1">
                <Bookmark size={12} />
                <span>Сохранена</span>
              </span>
            )}
          </div>
        </div>

        {aggregation.rating && (
          <div>
            <RatingStars rating={aggregation.rating} size={16} />
          </div>
        )}
      </div>

      <div className="mb-4">
        <div className="text-sm text-gray-500 mb-2">Характеристики группировки:</div>
        <div className="bg-gray-50 rounded-lg p-3 space-y-1">
          {Object.entries(aggregation.grouping_characteristics).map(([key, value]) => (
            <div key={key} className="text-sm">
              <span className="text-gray-600">{key}:</span>{' '}
              <span className="text-gray-900">{value || 'Не указано'}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="mb-4">
        <div className="text-sm text-gray-500 mb-2">СТЕ в группе: {aggregation.items_count}</div>
        <div className="flex space-x-2">
          {firstThreeItems.map((item) => (
            <div key={item.id} className="w-16 h-16 bg-gray-100 rounded border border-gray-200 flex items-center justify-center overflow-hidden">
              {item.ste.image_url ? (
                <ImageWithFallback
                  src={item.ste.image_url}
                  alt={item.ste.name}
                  className="w-full h-full object-cover"
                />
              ) : (
                <Package size={24} className="text-gray-400" />
              )}
            </div>
          ))}
          {aggregation.items_count > 3 && (
            <div className="w-16 h-16 bg-gray-100 rounded border border-gray-200 flex items-center justify-center">
              <span className="text-sm text-gray-600">+{aggregation.items_count - 3}</span>
            </div>
          )}
        </div>
      </div>

      <div className="flex items-center justify-between pt-4 border-t border-gray-100">
        <Link
          to={`/aggregations/${aggregation.id}`}
          className="px-4 py-2 bg-[rgb(219,43,33)] text-white rounded-lg hover:bg-[rgb(199,23,13)] transition-colors"
        >
          Открыть
        </Link>

        <div className="flex items-center space-x-2">
          {!aggregation.is_saved && onSave && (
            <button
              onClick={() => onSave(aggregation.id)}
              className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
              title="Сохранить"
            >
              <Bookmark size={20} />
            </button>
          )}
          {onDelete && (
            <button
              onClick={() => onDelete(aggregation.id)}
              className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
              title="Удалить"
            >
              <Trash2 size={20} />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
