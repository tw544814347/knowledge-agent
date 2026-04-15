const API_BASE = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL}/api/v1`
  : '/api/v1';

const HEALTH_BASE = import.meta.env.VITE_API_URL || '';

export async function askQuestion(question, topK = 8, signal) {
  const res = await fetch(`${API_BASE}/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, top_k: topK }),
    signal,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `请求失败 (${res.status})`);
  }
  return res.json();
}

export async function getStatus() {
  const res = await fetch(`${API_BASE}/status`);
  if (!res.ok) throw new Error('获取状态失败');
  return res.json();
}

export async function healthCheck() {
  const res = await fetch(`${HEALTH_BASE}/health`);
  if (!res.ok) throw new Error('服务不可用');
  return res.json();
}

export async function syncDocuments() {
  const res = await fetch(`${API_BASE}/sync`, { method: 'POST' });
  if (!res.ok) throw new Error('同步失败');
  return res.json();
}

export async function rebuildIndex() {
  const res = await fetch(`${API_BASE}/rebuild`, { method: 'POST' });
  if (!res.ok) throw new Error('重建索引失败');
  return res.json();
}

export async function askQuestionStream(question, topK = 8, signal, onChunk) {
  const res = await fetch(`${API_BASE}/ask/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, top_k: topK }),
    signal,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `请求失败 (${res.status})`);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop();

    for (const line of lines) {
      if (line.trim()) {
        try { onChunk(JSON.parse(line)); } catch { /* skip malformed */ }
      }
    }
  }

  if (buffer.trim()) {
    try { onChunk(JSON.parse(buffer)); } catch { /* skip */ }
  }
}
