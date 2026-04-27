import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getItem, updateItem, analyzeImage } from '../api';

const ITEM_TYPES = ['Top', 'Bottom', 'Outer', 'Shoe', 'Accessory'];

const FIELDS = [
  'description', 'fit', 'aesthetic', 'tone', 'layer', 'season',
  'color', 'pattern_style', 'material', 'gender_expression', 'formality', 'use_case',
] as const;

export default function Edit() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [form, setForm] = useState<Record<string, string>>({});
  const [imagePath, setImagePath] = useState('');
  const [preview, setPreview] = useState('');
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    getItem(Number(id)).then(item => {
      const f: Record<string, string> = {};
      for (const [k, v] of Object.entries(item)) {
        if (k === 'tags' && Array.isArray(v)) f[k] = v.join(', ');
        else if (k === 'image_path') setImagePath(v as string);
        else if (v != null) f[k] = String(v);
      }
      setForm(f);
      setPreview(item.image_path);
      setLoading(false);
    });
  }, [id]);

  const set = (key: string, val: string) => setForm(f => ({ ...f, [key]: val }));

  const handleFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setPreview(URL.createObjectURL(file));
    try {
      const data = await analyzeImage(file);
      if (!data.error) {
        const newForm: Record<string, string> = {};
        for (const [k, v] of Object.entries(data)) {
          if (k === 'tags' && Array.isArray(v)) newForm[k] = v.join(', ');
          else if (k === 'image_path') setImagePath(v as string);
          else if (k === 'item_type') newForm[k] = String(v).charAt(0).toUpperCase() + String(v).slice(1).toLowerCase();
          else newForm[k] = String(v);
        }
        setForm(f => ({ ...f, ...newForm }));
        if (data.image_path) setImagePath(data.image_path as string);
      }
    } catch { /* keep existing form data */ }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const tags = form.tags ? form.tags.split(',').map(t => t.trim()).filter(Boolean) : [];
      await updateItem(Number(id), { ...form, tags, image_path: imagePath } as any);
      navigate('/');
    } catch {
      alert('Failed to save item');
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <p>Loading...</p>;

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Edit Item</h1>

      <form onSubmit={handleSubmit}>
        {preview && (
          <img src={preview} alt="Preview" className="w-48 h-48 object-cover rounded mb-4" />
        )}

        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">Replace Photo</label>
          <input type="file" accept="image/*" onChange={handleFile} className="block w-full text-sm border rounded p-2" />
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">Name</label>
          <input value={form.name || ''} onChange={e => set('name', e.target.value)} className="w-full border rounded px-3 py-2" required />
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">Type</label>
          <select value={form.item_type || 'Top'} onChange={e => set('item_type', e.target.value)} className="w-full border rounded px-3 py-2">
            {ITEM_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
          </select>
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">Tags (comma-separated)</label>
          <input value={form.tags || ''} onChange={e => set('tags', e.target.value)} className="w-full border rounded px-3 py-2" />
        </div>

        {FIELDS.map(field => (
          <div key={field} className="mb-3">
            <label className="block text-sm font-medium mb-1 capitalize">{field.replace('_', ' ')}</label>
            <input value={form[field] || ''} onChange={e => set(field, e.target.value)} className="w-full border rounded px-3 py-2" />
          </div>
        ))}

        <button type="submit" disabled={saving} className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 disabled:opacity-50">
          {saving ? 'Saving...' : 'Save Changes'}
        </button>
      </form>
    </div>
  );
}
