import { X } from 'lucide-react';

interface HelpModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function HelpModal({ isOpen, onClose }: HelpModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <h2 className="text-2xl text-gray-900">Справочная информация для модератора</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X size={24} />
          </button>
        </div>

        <div className="p-6 space-y-8">
          {/* Цель сервиса */}
          <section>
            <h3 className="text-xl text-gray-900 mb-3 pb-2 border-b-2 border-[rgb(219,43,33)]">
              Цель сервиса
            </h3>
            <p className="text-gray-700 leading-relaxed">
              Автоматически объединять тысячи одинаковых товаров (СТЕ), загруженных поставщиками под разными названиями, в одну «эталонную» группу (агрегацию). Это позволяет городу видеть реальный объём закупок и экономить бюджет за счёт объединения лотов.
            </p>
          </section>

          {/* Как работать с сервисом */}
          <section>
            <h3 className="text-xl text-gray-900 mb-4 pb-2 border-b-2 border-[rgb(219,43,33)]">
              Как работать с сервисом (пошагово)
            </h3>

            <div className="space-y-6">
              {/* Шаг 1 */}
              <div className="bg-gray-50 rounded-lg p-5">
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-[rgb(219,43,33)] text-white rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                    1
                  </div>
                  <div className="flex-1">
                    <h4 className="text-lg text-gray-900 mb-3">Поиск СТЕ</h4>
                    <ul className="space-y-2 text-gray-700">
                      <li className="flex items-start">
                        <span className="text-[rgb(219,43,33)] mr-2">→</span>
                        <span>Введите в поисковую строку название товара, модель, производителя или часть характеристики (например, «шина», «256 мм», «Ozka», «ноутбук Lenovo»)</span>
                      </li>
                      <li className="flex items-start">
                        <span className="text-[rgb(219,43,33)] mr-2">→</span>
                        <span>Система автоматически начнёт поиск (с небольшой задержкой для удобства)</span>
                      </li>
                      <li className="flex items-start">
                        <span className="text-[rgb(219,43,33)] mr-2">→</span>
                        <span>Отметьте галочками нужные СТЕ для последующей группировки (опционально)</span>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>

              {/* Шаг 2 */}
              <div className="bg-gray-50 rounded-lg p-5">
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-[rgb(219,43,33)] text-white rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                    2
                  </div>
                  <div className="flex-1">
                    <h4 className="text-lg text-gray-900 mb-3">Запуск автоматической группировки</h4>
                    <p className="text-gray-700 mb-3">Варианты запуска:</p>
                    <ul className="space-y-2 text-gray-700">
                      <li className="flex items-start">
                        <span className="text-[rgb(219,43,33)] mr-2">•</span>
                        <span><strong>«Сгруппировать все СТЕ»</strong> (на странице Агрегации) — будет обработана вся база данных</span>
                      </li>
                      <li className="flex items-start">
                        <span className="text-[rgb(219,43,33)] mr-2">•</span>
                        <span><strong>«Сгруппировать выбранные»</strong> (на странице Поиска) — только отмеченные галочками товары</span>
                      </li>
                    </ul>
                    <div className="mt-3 p-3 bg-blue-50 border-l-4 border-blue-500 rounded">
                      <p className="text-sm text-blue-900">
                        <strong>Совет:</strong> Для повторной обработки уже сгруппированных СТЕ система автоматически использует параметр force_regenerate
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Шаг 3 */}
              <div className="bg-gray-50 rounded-lg p-5">
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-[rgb(219,43,33)] text-white rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                    3
                  </div>
                  <div className="flex-1">
                    <h4 className="text-lg text-gray-900 mb-3">Просмотр результатов группировки</h4>
                    <p className="text-gray-700 mb-3">Система покажет карточки готовых групп (агрегаций). В каждой карточке видно:</p>
                    <ul className="space-y-2 text-gray-700">
                      <li className="flex items-start">
                        <span className="text-[rgb(219,43,33)] mr-2">•</span>
                        <span>Автоматически сформированное название группы</span>
                      </li>
                      <li className="flex items-start">
                        <span className="text-[rgb(219,43,33)] mr-2">•</span>
                        <span>Значимые характеристики, по которым произошло объединение</span>
                      </li>
                      <li className="flex items-start">
                        <span className="text-[rgb(219,43,33)] mr-2">•</span>
                        <span>Количество СТЕ в группе</span>
                      </li>
                      <li className="flex items-start">
                        <span className="text-[rgb(219,43,33)] mr-2">•</span>
                        <span>Первые несколько миниатюр товаров</span>
                      </li>
                      <li className="flex items-start">
                        <span className="text-[rgb(219,43,33)] mr-2">•</span>
                        <span>Среднюю оценку пользователей (если уже оценивали)</span>
                      </li>
                      <li className="flex items-start">
                        <span className="text-[rgb(219,43,33)] mr-2">•</span>
                        <span>Метки: «Автоматическая» / «Ручная», «Сохранена» (зелёная метка)</span>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>

              {/* Шаг 4 */}
              <div className="bg-yellow-50 rounded-lg p-5 border-2 border-yellow-400">
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-[rgb(219,43,33)] text-white rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                    4
                  </div>
                  <div className="flex-1">
                    <h4 className="text-lg text-gray-900 mb-3">Ручное улучшение группы (самое важное!)</h4>
                    <p className="text-gray-700 mb-3">Откройте любую группу → кнопка <strong>«Открыть»</strong>. Здесь вы можете:</p>
                    <ul className="space-y-2 text-gray-700">
                      <li className="flex items-start">
                        <span className="text-[rgb(219,43,33)] mr-2">•</span>
                        <span><strong>Удалить ошибочно попавшие СТЕ</strong> → красная иконка корзины напротив товара</span>
                      </li>
                      <li className="flex items-start">
                        <span className="text-[rgb(219,43,33)] mr-2">•</span>
                        <span><strong>Изменить порядок СТЕ</strong> → стрелки вверх/вниз напротив каждой СТЕ</span>
                      </li>
                      <li className="flex items-start">
                        <span className="text-[rgb(219,43,33)] mr-2">•</span>
                        <span><strong>Поставить свою оценку</strong> (1–5 звёзд) и написать комментарий внизу страницы</span>
                      </li>
                      <li className="flex items-start">
                        <span className="text-[rgb(219,43,33)] mr-2">•</span>
                        <span><strong>Нажать «Сохранить агрегацию»</strong> (зелёная кнопка сверху) — после этого группа становится эталонной</span>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>

              {/* Шаг 5 */}
              <div className="bg-gray-50 rounded-lg p-5">
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-[rgb(219,43,33)] text-white rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                    5
                  </div>
                  <div className="flex-1">
                    <h4 className="text-lg text-gray-900 mb-3">Что значит «Сохранена»</h4>
                    <div className="p-4 bg-green-50 border-l-4 border-green-500 rounded">
                      <p className="text-gray-700">
                        Только сохранённые вручную агрегации считаются «проверенными модератором» и в дальнейшем используются как эталон в каталоге Портала поставщиков. Несохранённые группы — это автоматические предложения системы, которые требуют вашей проверки.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* Как быстро найти проблемные группы */}
          <section className="bg-blue-50 rounded-lg p-5">
            <h3 className="text-lg text-gray-900 mb-3">💡 Как быстро найти проблемные группы</h3>
            <p className="text-gray-700">
              На странице со списком агрегаций используйте галочку <strong>«Показать только сохраненные»</strong> — снимите её, чтобы увидеть несохранённые группы, которые требуют вашего внимания и проверки.
            </p>
          </section>

          {/* Полезные советы */}
          <section>
            <h3 className="text-xl text-gray-900 mb-4 pb-2 border-b-2 border-[rgb(219,43,33)]">
              Полезные советы
            </h3>
            <div className="space-y-3">
              <div className="flex items-start space-x-3 p-3 bg-red-50 rounded-lg">
                <span className="text-xl">⭐</span>
                <p className="text-gray-700">
                  Если группа собрана плохо — поставьте низкую оценку (1–2 звезды) и отредактируйте вручную. Это поможет алгоритму учиться.
                </p>
              </div>
              <div className="flex items-start space-x-3 p-3 bg-green-50 rounded-lg">
                <span className="text-xl">🌟</span>
                <p className="text-gray-700">
                  Если группа идеальная — поставьте 5 звёзд и сразу сохраните.
                </p>
              </div>
              <div className="flex items-start space-x-3 p-3 bg-yellow-50 rounded-lg">
                <span className="text-xl">📊</span>
                <p className="text-gray-700">
                  Группы с высоким средним рейтингом показывают качество автоматической группировки.
                </p>
              </div>
              <div className="flex items-start space-x-3 p-3 bg-purple-50 rounded-lg">
                <span className="text-xl">🔍</span>
                <p className="text-gray-700">
                  Проверяйте характеристики группировки — это ключевые параметры, по которым товары были объединены. Они должны быть действительно значимыми для данной категории.
                </p>
              </div>
              <div className="flex items-start space-x-3 p-3 bg-orange-50 rounded-lg">
                <span className="text-xl">🗑️</span>
                <p className="text-gray-700">
                  Не бойтесь удалять неудачные агрегации целиком (красная кнопка «Удалить»). Их можно будет создать заново с помощью повторной группировки.
                </p>
              </div>
            </div>
          </section>

          {/* Workflow схема */}
          <section className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-5 border-2 border-blue-200">
            <h3 className="text-lg text-gray-900 mb-4 text-center">Типичный workflow модератора</h3>
            <div className="flex items-center justify-center space-x-2 flex-wrap">
              <div className="bg-white px-4 py-2 rounded-lg shadow text-center m-1">
                <div className="text-sm text-gray-600">1. Запустить</div>
                <div className="text-[rgb(219,43,33)]">Группировку</div>
              </div>
              <div className="text-2xl text-gray-400">→</div>
              <div className="bg-white px-4 py-2 rounded-lg shadow text-center m-1">
                <div className="text-sm text-gray-600">2. Открыть</div>
                <div className="text-[rgb(219,43,33)]">Агрегацию</div>
              </div>
              <div className="text-2xl text-gray-400">→</div>
              <div className="bg-white px-4 py-2 rounded-lg shadow text-center m-1">
                <div className="text-sm text-gray-600">3. Проверить</div>
                <div className="text-[rgb(219,43,33)]">Состав</div>
              </div>
              <div className="text-2xl text-gray-400">→</div>
              <div className="bg-white px-4 py-2 rounded-lg shadow text-center m-1">
                <div className="text-sm text-gray-600">4. Оценить</div>
                <div className="text-[rgb(219,43,33)]">1-5 звёзд</div>
              </div>
              <div className="text-2xl text-gray-400">→</div>
              <div className="bg-white px-4 py-2 rounded-lg shadow text-center m-1">
                <div className="text-sm text-gray-600">5. Нажать</div>
                <div className="text-[rgb(219,43,33)]">Сохранить</div>
              </div>
            </div>
          </section>
        </div>

        <div className="sticky bottom-0 bg-gray-50 border-t border-gray-200 px-6 py-4 flex justify-end">
          <button
            onClick={onClose}
            className="px-6 py-3 bg-[rgb(219,43,33)] text-white rounded-lg hover:bg-[rgb(199,23,13)] transition-colors"
          >
            Понятно, закрыть
          </button>
        </div>
      </div>
    </div>
  );
}
