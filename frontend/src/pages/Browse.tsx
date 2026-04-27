import { useEffect, useState } from 'react';
import { fetchItems, deleteItem, type Item } from '../api';

const TYPES = ['', 'Top', 'Bottom', 'Outer', 'Shoe', 'Accessory'];

export default function Browse() {
  const [items, setItems] = useState<Item[]>([]);
  const [filter, setFilter] = useState('');

  const load = () => fetchItems(filter || undefined).then(setItems);

  useEffect(() => { load(); }, [filter]);

  const handleDelete = async (id: number) => {
    if (!confirm('Delete this item?')) return;
    await deleteItem(id);
    load();
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Your Wardrobe</h1>
        <select
          value={filter}
          onChange={e => setFilter(e.target.value)}
          className="border rounded px-3 py-2"
        >
          {TYPES.map(t => (
            <option key={t} value={t}>{t || 'All Types'}</option>
          ))}
        </select>
      </div>

      {items.length === 0 && (
        <p className="text-gray-500">No items yet. Upload some clothes!</p>
      )}

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {items.map(item => (
          <div key={item.id} className="border rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-shadow">
            {item.image_path && (
              <img
                src={item.image_path}
                alt={item.name}
                className="w-full h-48 object-cover"
              />
            )}
            <div className="p-3">
              <h3 className="font-semibold">{item.name}</h3>
              <p className="text-sm text-gray-500">{item.item_type}</p>
              <div className="flex gap-2 mt-2">
                <a
                  href={`/edit/${item.id}`}
                  className="text-sm text-blue-600 hover:underline"
                >
                  Edit
                </a>
                <button
                  onClick={() => handleDelete(item.id)}
                  className="text-sm text-red-600 hover:underline"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
