const API_BASE = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL}/api/v1`
  : '/api/v1';

const HEALTH_BASE = import.meta.env.VITE_API_URL || '';

const NGROK_HEADERS = import.meta.env.VITE_API_URL?.includes('ngrok')
  ? { 'ngrok-skip-browser-warning': 'true' }
  : {};

export async function askQuestion(question, topK = 8, signal) {
  const res = await fetch(`${API_BASE}/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...NGROK_HEADERS },
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
  const res = await fetch(`${API_BASE}/status`, { headers: NGROK_HEADERS });
  if (!res.ok) throw new Error('获取状态失败');
  return res.json();
}

export async function healthCheck() {
  const res = await fetch(`${HEALTH_BASE}/health`, { headers: NGROK_HEADERS });
  if (!res.ok) throw new Error('服务不可用');
  return res.json();
}

export async function syncDocuments() {
  const res = await fetch(`${API_BASE}/sync`, { method: 'POST', headers: NGROK_HEADERS });
  if (!res.ok) throw new Error('同步失败');
  return res.json();
}

export async function rebuildIndex() {
  const res = await fetch(`${API_BASE}/rebuild`, { method: 'POST', headers: NGROK_HEADERS });
  if (!res.ok) throw new Error('重建索引失败');
  return res.json();
}

export async function askQuestionStream(question, topK = 8, signal, onChunk, conversationId = null) {
  const token = localStorage.getItem('access_token');
  const headers = { 
    'Content-Type': 'application/json', 
    ...NGROK_HEADERS 
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  const requestBody = { question, top_k: topK };
  if (conversationId) {
    requestBody.conversation_id = conversationId;
  }
  
  const res = await fetch(`${API_BASE}/ask/stream`, {
    method: 'POST',
    headers,
    body: JSON.stringify(requestBody),
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

// 对话历史相关 API
const HEADERS = { 'Content-Type': 'application/json', ...NGROK_HEADERS };

export const getConversations = async (limit = 10) => {
  const token = localStorage.getItem('access_token');
  const response = await fetch(`${API_BASE}/conversations?limit=${limit}`, {
    headers: {
      ...NGROK_HEADERS,
      'Authorization': `Bearer ${token}`
    },
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return await response.json();
};

export const getConversation = async (conversationId) => {
  const response = await fetch(`${API_BASE}/conversations/${conversationId}`, {
    headers: NGROK_HEADERS,
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return await response.json();
};

export const createConversation = async (question, answer, sources = []) => {
  const token = localStorage.getItem('access_token');
  const response = await fetch(`${API_BASE}/conversations`, {
    method: 'POST',
    headers: {
      ...HEADERS,
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      question,
      answer,
      sources,
    }),
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return await response.json();
};

export const updateConversation = async (conversationId, updates) => {
  const token = localStorage.getItem('access_token');
  const response = await fetch(`${API_BASE}/conversations/${conversationId}`, {
    method: 'PUT',
    headers: {
      ...HEADERS,
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(updates),
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return await response.json();
};

export const deleteConversation = async (conversationId) => {
  const token = localStorage.getItem('access_token');
  const response = await fetch(`${API_BASE}/conversations/${conversationId}`, {
    method: 'DELETE',
    headers: {
      ...NGROK_HEADERS,
      'Authorization': `Bearer ${token}`
    },
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return await response.json();
};

// 用户认证相关 API
export const register = async (email, password, nickname) => {
  const response = await fetch(`${API_BASE}/auth/register`, {
    method: 'POST',
    headers: HEADERS,
    body: JSON.stringify({ email, password, nickname }),
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return await response.json();
};

export const login = async (email, password) => {
  const response = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: HEADERS,
    body: JSON.stringify({ email, password }),
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  const data = await response.json();
  
  // 保存token到localStorage
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('user', JSON.stringify(data.user));
  
  return data;
};

export const logout = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('user');
};

export const getCurrentUser = () => {
  const userStr = localStorage.getItem('user');
  return userStr ? JSON.parse(userStr) : null;
};

export const isAuthenticated = () => {
  return !!localStorage.getItem('access_token');
};

// 新对话功能
export const newChat = async () => {
  const token = localStorage.getItem('access_token');
  const response = await fetch(`${API_BASE}/chat/new`, {
    method: 'POST',
    headers: {
      ...HEADERS,
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ clear_current: true }),
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return await response.json();
};

// Ask tool integration
export const sendAskResponse = async (question, selectedOption, optionIndex) => {
  const response = await fetch(`${API_BASE}/ask/response`, {
    method: 'POST',
    headers: HEADERS,
    body: JSON.stringify({
      question,
      selected_option: selectedOption,
      option_index: optionIndex
    })
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return await response.json();
};

// 忘记密码功能
export const forgotPassword = async (email) => {
  const response = await fetch(`${API_BASE}/auth/forgot-password`, {
    method: 'POST',
    headers: HEADERS,
    body: JSON.stringify({ email })
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return await response.json();
};

export const resetPassword = async (email, resetCode, newPassword) => {
  const response = await fetch(`${API_BASE}/auth/reset-password`, {
    method: 'POST',
    headers: HEADERS,
    body: JSON.stringify({
      email,
      reset_code: resetCode,
      new_password: newPassword
    })
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return await response.json();
};

// 修改密码（已登录用户）
export const changePassword = async (currentPassword, newPassword) => {
  const token = localStorage.getItem('access_token');
  if (!token) {
    throw new Error('请先登录');
  }

  const response = await fetch(`${API_BASE}/auth/change-password`, {
    method: 'POST',
    headers: {
      ...HEADERS,
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({
      current_password: currentPassword,
      new_password: newPassword
    })
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return await response.json();
};

// 发送注册验证码
export const sendRegistrationCode = async (email) => {
  const response = await fetch(`${API_BASE}/auth/send-registration-code`, {
    method: 'POST',
    headers: HEADERS,
    body: JSON.stringify({ email })
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return await response.json();
};

// 验证注册
export const verifyRegistration = async (email, verificationCode, password, nickname) => {
  const response = await fetch(`${API_BASE}/auth/verify-registration`, {
    method: 'POST',
    headers: HEADERS,
    body: JSON.stringify({
      email,
      verification_code: verificationCode,
      password,
      nickname
    })
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  const data = await response.json();
  // 与 login 一致：注册成功后必须持久化 token，否则依赖 Authorization 的接口会 401
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('user', JSON.stringify(data.user));
  return data;
};

export const checkAskRequests = async () => {
  const response = await fetch(`${API_BASE}/ask/check`, {
    method: 'GET',
    headers: HEADERS,
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return await response.json();
};
