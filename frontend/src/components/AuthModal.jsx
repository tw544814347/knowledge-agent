import { useState } from 'react';
import { X, Mail, Lock, User } from 'lucide-react';
import { login, register } from '../api';

export default function AuthModal({ onClose, onAuthSuccess }) {
  const [isLogin, setIsLogin] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    nickname: ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      let result;
      if (isLogin) {
        result = await login(formData.email, formData.password);
        onAuthSuccess(result.user);
        onClose();
      } else {
        // 注册成功后不直接关闭，而是切换到登录模式
        result = await register(formData.email, formData.password, formData.nickname);
        // 注册成功，切换到登录界面
        setIsLogin(true);
        setFormData(prev => ({ ...prev, password: '', nickname: '' }));
        setError(''); 
        // 显示成功提示
        setTimeout(() => {
          setError('注册成功，请登录');
        }, 100);
      }
    } catch (err) {
      // 提取更友好的错误信息
      let errorMessage = err.message || '操作失败';
      if (errorMessage.includes('注册失败:')) {
        errorMessage = errorMessage.replace('注册失败: ', '');
      }
      if (errorMessage.includes('HTTP 400') || errorMessage.includes('HTTP 500')) {
        errorMessage = isLogin ? '登录失败，请检查邮箱和密码' : '注册失败，请稍后重试';
      }
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-[var(--color-dark-800)] rounded-xl shadow-xl w-full max-w-md mx-4 border border-[var(--color-border)]">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-[var(--color-border)]">
          <h2 className="text-xl font-semibold text-[var(--color-text-primary)]">
            {isLogin ? '登录' : '注册'}
          </h2>
          <button
            onClick={onClose}
            className="p-1 rounded hover:bg-[var(--color-dark-600)] text-[var(--color-text-secondary)]"
          >
            <X size={20} />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {/* Email */}
          <div>
            <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
              邮箱地址
            </label>
            <div className="relative">
              <Mail size={18} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-[var(--color-text-muted)]" />
              <input
                type="email"
                required
                value={formData.email}
                onChange={(e) => handleInputChange('email', e.target.value)}
                placeholder="your.email@example.com"
                className="w-full pl-10 pr-3 py-2.5 bg-[var(--color-dark-700)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] placeholder-[var(--color-text-muted)] focus:outline-none focus:border-[var(--color-primary)] transition-colors"
              />
            </div>
          </div>

          {/* Password */}
          <div>
            <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
              密码
            </label>
            <div className="relative">
              <Lock size={18} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-[var(--color-text-muted)]" />
              <input
                type="password"
                required
                minLength={6}
                value={formData.password}
                onChange={(e) => handleInputChange('password', e.target.value)}
                placeholder="至少6位密码"
                className="w-full pl-10 pr-3 py-2.5 bg-[var(--color-dark-700)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] placeholder-[var(--color-text-muted)] focus:outline-none focus:border-[var(--color-primary)] transition-colors"
              />
            </div>
          </div>

          {/* Nickname (register only) */}
          {!isLogin && (
            <div>
              <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
                昵称（可选）
              </label>
              <div className="relative">
                <User size={18} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-[var(--color-text-muted)]" />
                <input
                  type="text"
                  value={formData.nickname}
                  onChange={(e) => handleInputChange('nickname', e.target.value)}
                  placeholder="设置一个昵称"
                  className="w-full pl-10 pr-3 py-2.5 bg-[var(--color-dark-700)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] placeholder-[var(--color-text-muted)] focus:outline-none focus:border-[var(--color-primary)] transition-colors"
                />
              </div>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="text-red-400 text-sm bg-red-900/20 p-3 rounded-lg">
              {error}
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors"
          >
            {loading ? (isLogin ? '登录中...' : '注册中...') : (isLogin ? '登录' : '注册')}
          </button>

          {/* Switch Mode */}
          <div className="text-center pt-4 border-t border-[var(--color-border)]">
            <span className="text-sm text-[var(--color-text-muted)]">
              {isLogin ? '还没有账号？' : '已有账号？'}
            </span>
            <button
              type="button"
              onClick={() => setIsLogin(!isLogin)}
              className="ml-2 text-sm text-[var(--color-primary)] hover:underline"
            >
              {isLogin ? '立即注册' : '立即登录'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}