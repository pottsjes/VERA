const BASE = import.meta.env.VITE_API_URL ?? '';

export interface Item {
  id: number;
  name: string;
  item_type: string;
  description: string;
  tags: string[];
  image_path: string;
  available: boolean;
  last_used: string | null;
  nfc_tag_id: string | null;
  fit: string;
  aesthetic: string;
  tone: string;
  layer: string;
  season: string;
  color: string;
  pattern_style: string;
  material: string;
  gender_expression: string;
  formality: string;
  use_case: string;
}

export interface RecommendResponse {
  vibe: string;
  items: Item[];
  reasoning: string;
  styling_tips: string | null;
}

export async function fetchItems(itemType?: string): Promise<Item[]> {
  const params = itemType ? `?item_type=${itemType}` : '';
  const res = await fetch(`${BASE}/api/items/${params}`);
  return res.json();
}

export async function getItem(id: number): Promise<Item> {
  const res = await fetch(`${BASE}/api/items/${id}`);
  return res.json();
}

export async function createItem(data: Partial<Item>): Promise<Item> {
  const res = await fetch(`${BASE}/api/items/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function updateItem(id: number, data: Partial<Item>): Promise<Item> {
  const res = await fetch(`${BASE}/api/items/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function deleteItem(id: number): Promise<void> {
  await fetch(`${BASE}/api/items/${id}`, { method: 'DELETE' });
}

export async function analyzeImage(file: File): Promise<Record<string, unknown>> {
  const form = new FormData();
  form.append('image', file);
  const res = await fetch(`${BASE}/api/analyze-image`, { method: 'POST', body: form });
  return res.json();
}

export async function recommend(vibe: string): Promise<RecommendResponse> {
  const res = await fetch(`${BASE}/api/recommend/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ vibe }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Request failed (${res.status})`);
  }
  return res.json();
}
