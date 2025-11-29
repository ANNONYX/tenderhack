import { Link } from 'react-router-dom';
import { STEResponse } from '../../types';
import { ImageWithFallback } from '../figma/ImageWithFallback';
import { Package } from 'lucide-react';

interface STECardProps {
  ste: STEResponse;
  isSelected?: boolean;
  onSelect?: (id: number) => void;
  showCheckbox?: boolean;
}

export function STECard({ ste, isSelected, onSelect, showCheckbox }: STECardProps) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 hover:shadow-lg transition-shadow overflow-hidden">
      <Link to={`/ste/${ste.id}`} className="block">
        <div className="aspect-square bg-gray-100 flex items-center justify-center overflow-hidden">
          {ste.image_url ? (
            <ImageWithFallback
              src={ste.image_url}
              alt={ste.name}
              className="w-full h-full object-cover"
            />
          ) : (
            <Package size={48} className="text-gray-400" />
          )}
        </div>
      </Link>

      <div className="p-4">
        {showCheckbox && (
          <div className="mb-3">
            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={isSelected}
                onChange={() => onSelect?.(ste.id)}
                className="w-4 h-4 text-[rgb(219,43,33)] border-gray-300 rounded focus:ring-[rgb(219,43,33)]"
                onClick={(e) => e.stopPropagation()}
              />
              <span className="text-sm text-gray-600">Выбрать для группировки</span>
            </label>
          </div>
        )}

        <Link to={`/ste/${ste.id}`}>
          <h3 className="text-gray-900 hover:text-[rgb(219,43,33)] transition-colors line-clamp-2 mb-2">
            {ste.name}
          </h3>
        </Link>

        <div className="space-y-1 text-sm text-gray-600">
          {ste.manufacturer && (
            <div>
              <span className="text-gray-500">Производитель:</span> {ste.manufacturer}
            </div>
          )}
          {ste.model && (
            <div>
              <span className="text-gray-500">Модель:</span> {ste.model}
            </div>
          )}
          <div className="text-xs text-gray-500 mt-2 line-clamp-1">
            {ste.category_name}
          </div>
        </div>

        <div className="mt-3 pt-3 border-t border-gray-100">
          <div className="text-xs text-gray-500">
            ID: {ste.ste_id}
          </div>
        </div>
      </div>
    </div>
  );
}
