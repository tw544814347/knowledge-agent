import { useState } from 'react';
import { X, Lock, CheckCircle } from 'lucide-react';
import { changePassword } from '../api';

export default function ChangePasswordModal({ user, onClose, onSuccess }) {
  const [formData, setFormData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setError('');
    setSuccess('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    // 验证新密码
    if (formData.newPassword.length < 6) {
      setError('新密码至少需要6位');
      setLoading(false);
      return;
    }

    if (formData.newPassword !== formData.confirmPassword) {
      setError('两次输入的新密码不一致');
      setLoading(false);
      return;
    }

    if (formData.currentPassword === formData.newPassword) {
      setError('新密码不能与当前密码相同');
      setLoading(false);
      return;
    }

    try {
      await changePassword(formData.currentPassword, formData.newPassword);
      setSuccess('密码修改成功！');
      
      // 2秒后关闭弹窗
      setTimeout(() => {
        onSuccess?.();
        onClose();
      }, 2000);
    } catch (err) {
      let errorMessage = err.message || '密码修改失败';
      if (errorMessage.includes('HTTP 400')) {
        errorMessage = '当前密码不正确';
      } else if (errorMessage.includes('HTTP 401')) {
        errorMessage = '请重新登录';
      }
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-[var(--color-dark-800)] rounded-xl shadow-xl w-full max-w-md mx-4 border border-[var(--color-border)]">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-[var(--color-border)]">
          <h2 className="text-xl font-semibold text-[var(--color-text-primary)]">
            修改密码
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
          {/* User Info */}
          <div className="text-sm text-[var(--color-text-muted)] mb-4">
            正在为 <span className="font-medium text-[var(--color-text-primary)]">{user?.email}</span> 修改密码
          </div>

          {/* Current Password */}
          <div>
            <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
              当前密码
            </label>
            <div className="relative">
              <Lock size={18} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-[var(--color-text-muted)]" />
              <input
                type="password"
                required
                value={formData.currentPassword}
                onChange={(e) => handleInputChange('currentPassword', e.target.value)}
                placeholder="请输入当前密码"
                className="w-full pl-10 pr-3 py-2.5 bg-[var(--color-dark-700)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] placeholder-[var(--color-text-muted)] focus:outline-none focus:border-[var(--color-primary)] transition-colors"
              />
            </div>
          </div>

          {/* New Password */}
          <div>
            <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
              新密码
            </label>
            <div className="relative">
              <Lock size={18} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-[var(--color-text-muted)]" />
              <input
                type="password"
                required
                minLength={6}
                value={formData.newPassword}
                onChange={(e) => handleInputChange('newPassword', e.target.value)}
                placeholder="请输入新密码（至少6位）"
                className="w-full pl-10 pr-3 py-2.5 bg-[var(--color-dark-700)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] placeholder-[var(--color-text-muted)] focus:outline-none focus:border-[var(--color-primary)] transition-colors"
              />
            </div>
          </div>

          {/* Confirm Password */}
          <div>
            <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
              确认新密码
            </label>
            <div className="relative">
              <Lock size={18} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-[var(--color-text-muted)]" />
              <input
                type="password"
                required
                minLength={6}
                value={formData.confirmPassword}
                onChange={(e) => handleInputChange('confirmPassword', e.target.value)}
                placeholder="请再次输入新密码"
                className="w-full pl-10 pr-3 py-2.5 bg-[var(--color-dark-700)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] placeholder-[var(--color-text-muted)] focus:outline-none focus:border-[var(--color-primary)] transition-colors"
              />
            </div>
          </div>

          {/* Success Message */}
          {success && (
            <div className="flex items-center gap-2 text-green-400 text-sm bg-green-900/20 p-3 rounded-lg">
              <CheckCircle size={16} />
              {success}
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
            {loading ? '修改中...' : '修改密码'}
          </button>
        </form>
      </div>
    </div>
  );
}