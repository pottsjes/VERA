import { useState } from 'react';
import { recommend, type RecommendResponse } from '../api';

const PRESETS = ['casual friday', 'date night', 'summer festival', 'cozy winter', 'gym fit', 'streetwear'];

export default function Recommend() {
  const [vibe, setVibe] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<RecommendResponse | null>(null);
  const [error, setError] = useState('');

  const handleSubmit = async (vibeText?: string) => {
    const query = vibeText || vibe;
    if (!query.trim()) return;
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const data = await recommend(query);
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to get recommendation. Make sure you have items in your wardrobe!');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-2">What's the vibe?</h1>
      <p className="text-gray-500 mb-6">Describe the look you're going for and V.E.R.A. will pick an outfit from your wardrobe.</p>

      <div className="flex gap-2 mb-4">
        <input
          value={vibe}
          onChange={e => setVibe(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleSubmit()}
          placeholder="relaxed gen z summer fit..."
          className="flex-1 border rounded px-4 py-3 text-lg"
        />
        <button
          onClick={() => handleSubmit()}
          disabled={loading || !vibe.trim()}
          className="bg-blue-600 text-white px-6 py-3 rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? 'Styling...' : 'Go'}
        </button>
      </div>

      <div className="flex flex-wrap gap-2 mb-8">
        {PRESETS.map(p => (
          <button
            key={p}
            onClick={() => { setVibe(p); handleSubmit(p); }}
            className="px-3 py-1 bg-gray-100 rounded-full text-sm hover:bg-gray-200"
          >
            {p}
          </button>
        ))}
      </div>

      {error && <p className="text-red-600 mb-4">{error}</p>}

      {loading && (
        <div className="flex items-center gap-3 text-blue-600">
          <div className="animate-spin h-6 w-6 border-2 border-blue-600 border-t-transparent rounded-full" />
          Finding the perfect outfit...
        </div>
      )}

      {result && (
        <div>
          <div className="bg-gray-50 rounded-lg p-4 mb-6">
            <p className="text-gray-700">{result.reasoning}</p>
            {result.styling_tips && (
              <p className="text-sm text-gray-500 mt-2">💡 {result.styling_tips}</p>
            )}
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {result.items.map(item => (
              <div key={item.id} className="border rounded-lg overflow-hidden">
                {item.image_path && (
                  <img src={item.image_path} alt={item.name} className="w-full h-48 object-cover" />
                )}
                <div className="p-3">
                  <h3 className="font-semibold">{item.name}</h3>
                  <p className="text-sm text-gray-500">{item.item_type}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
