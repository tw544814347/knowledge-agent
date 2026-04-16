import { useState } from 'react';
import { X, Mail, Lock, User, Key, ArrowLeft } from 'lucide-react';
import { login, register, forgotPassword, resetPassword, sendRegistrationCode, verifyRegistration } from '../api';

export default function AuthModal({ onClose, onAuthSuccess }) {
  const [isLogin, setIsLogin] = useState(true);
  const [isForgotPassword, setIsForgotPassword] = useState(false);
  const [isResetPassword, setIsResetPassword] = useState(false);
  const [isEmailVerification, setIsEmailVerification] = useState(false); // 注册邮箱验证步骤
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    nickname: '',
    resetCode: '',
    newPassword: '',
    verificationCode: '' // 注册验证码
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      let result;
      
      if (isForgotPassword) {
        // 忘记密码 - 发送验证码
        result = await forgotPassword(formData.email);
        setSuccess('验证码已发送到您的邮箱（开发模式：请查看控制台）');
        setIsResetPassword(true);
        setIsForgotPassword(false);
      } else if (isResetPassword) {
        // 重置密码
        result = await resetPassword(formData.email, formData.resetCode, formData.newPassword);
        setSuccess('密码重置成功！');
        // 3秒后回到登录界面
        setTimeout(() => {
          setIsResetPassword(false);
          setIsLogin(true);
          setFormData({ email: formData.email, password: '', nickname: '', resetCode: '', newPassword: '' });
          setSuccess('');
        }, 3000);
      } else if (isLogin) {
        // 登录
        result = await login(formData.email, formData.password);
        onAuthSuccess(result.user);
        onClose();
      } else if (isEmailVerification) {
        // 验证注册（第二步）
        result = await verifyRegistration(
          formData.email,
          formData.verificationCode,
          formData.password,
          formData.nickname
        );
        onAuthSuccess(result.user);
        onClose();
      } else {
        // 发送注册验证码（第一步）
        result = await sendRegistrationCode(formData.email);
        setIsEmailVerification(true);
        setSuccess('验证码已发送到您的邮箱，请查收并输入验证码');
      }
    } catch (err) {
      let errorMessage = err.message || '操作失败';
      
      // 处理具体的错误信息
      if (errorMessage.includes('邮箱或密码错误')) {
        errorMessage = '密码错误，请重试';
      } else if (errorMessage.includes('注册失败:')) {
        errorMessage = errorMessage.replace('注册失败: ', '');
      } else if (errorMessage.includes('HTTP 401') && isLogin) {
        errorMessage = '密码错误，请重试';
      } else if (errorMessage.includes('HTTP 400')) {
        if (isForgotPassword) {
          errorMessage = '发送验证码失败，请检查邮箱地址';
        } else if (isResetPassword) {
          errorMessage = '密码重置失败，请检查验证码是否正确或已过期';
        } else if (isLogin) {
          errorMessage = '登录失败，请检查邮箱和密码';
        } else {
          errorMessage = '注册失败，邮箱可能已被注册';
        }
      } else if (errorMessage.includes('HTTP 500')) {
        if (isForgotPassword) {
          errorMessage = '邮件发送失败，请稍后重试';
        } else if (isResetPassword) {
          errorMessage = '密码重置失败，请稍后重试';
        } else if (isLogin) {
          errorMessage = '登录服务暂时不可用，请稍后重试';
        } else {
          errorMessage = '注册服务暂时不可用，请稍后重试';
        }
      }
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setError(''); // Clear error when user starts typing
    setSuccess(''); // Clear success message when user starts typing
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-[var(--color-dark-800)] rounded-xl shadow-xl w-full max-w-md mx-4 border border-[var(--color-border)]">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-[var(--color-border)]">
          <div className="flex items-center gap-2">
            {(isForgotPassword || isResetPassword || isEmailVerification) && (
              <button
                onClick={() => {
                  if (isEmailVerification) {
                    setIsEmailVerification(false);
                    setIsLogin(false); // 回到注册第一步
                  } else {
                    setIsForgotPassword(false);
                    setIsResetPassword(false);
                    setIsLogin(true);
                  }
                  setError('');
                  setSuccess('');
                }}
                className="p-1 rounded hover:bg-[var(--color-dark-600)] text-[var(--color-text-secondary)]"
              >
                <ArrowLeft size={18} />
              </button>
            )}
            <h2 className="text-xl font-semibold text-[var(--color-text-primary)]">
              {isForgotPassword ? '忘记密码' : 
               isResetPassword ? '重置密码' : 
               isEmailVerification ? '邮箱验证' :
               isLogin ? '登录' : '注册'}
            </h2>
          </div>
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

          {/* 验证码字段 - 重置密码或注册验证时显示 */}
          {(isResetPassword || isEmailVerification) && (
            <div>
              <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
                {isEmailVerification ? '邮箱验证码' : '验证码'}
              </label>
              <div className="relative">
                <Key size={18} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-[var(--color-text-muted)]" />
                <input
                  type="text"
                  required
                  value={isEmailVerification ? formData.verificationCode : formData.resetCode}
                  onChange={(e) => handleInputChange(isEmailVerification ? 'verificationCode' : 'resetCode', e.target.value)}
                  placeholder="请输入6位验证码"
                  className="w-full pl-10 pr-3 py-2.5 bg-[var(--color-dark-700)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] placeholder-[var(--color-text-muted)] focus:outline-none focus:border-[var(--color-primary)] transition-colors"
                />
              </div>
            </div>
          )}

          {/* Password - 忘记密码时不显示 */}
          {!isForgotPassword && (
            <div>
              <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
                {isResetPassword ? '新密码' : '密码'}
              </label>
              <div className="relative">
                <Lock size={18} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-[var(--color-text-muted)]" />
                <input
                  type="password"
                  required
                  minLength={6}
                  value={isResetPassword ? formData.newPassword : formData.password}
                  onChange={(e) => handleInputChange(isResetPassword ? 'newPassword' : 'password', e.target.value)}
                  placeholder={isResetPassword ? '设置新密码（至少6位）' : '至少6位密码'}
                  className="w-full pl-10 pr-3 py-2.5 bg-[var(--color-dark-700)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] placeholder-[var(--color-text-muted)] focus:outline-none focus:border-[var(--color-primary)] transition-colors"
                />
              </div>
            </div>
          )}

          {/* Nickname (register only) - 注册第一步和验证步骤都显示 */}
          {!isLogin && !isForgotPassword && !isResetPassword && (
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

          {/* Success Message */}
          {success && (
            <div className="text-green-400 text-sm bg-green-900/20 p-3 rounded-lg">
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
            {loading ? 
              (isForgotPassword ? '发送中...' : 
               isResetPassword ? '重置中...' : 
               isEmailVerification ? '验证中...' :
               isLogin ? '登录中...' : '发送验证码中...') : 
              (isForgotPassword ? '发送验证码' : 
               isResetPassword ? '重置密码' : 
               isEmailVerification ? '完成注册' :
               isLogin ? '登录' : '发送验证码')}
          </button>

          {/* Switch Mode and Options */}
          {!isForgotPassword && !isResetPassword && !isEmailVerification && (
            <div className="text-center pt-4 border-t border-[var(--color-border)] space-y-2">
              {/* 忘记密码链接 - 仅登录页面显示 */}
              {isLogin && (
                <div>
                  <button
                    type="button"
                    onClick={() => {
                      setIsForgotPassword(true);
                      setIsLogin(false);
                      setError('');
                      setSuccess('');
                    }}
                    className="text-sm text-[var(--color-primary)] hover:underline"
                  >
                    忘记密码？
                  </button>
                </div>
              )}
              
              {/* 登录/注册切换 */}
              <div>
                <span className="text-sm text-[var(--color-text-muted)]">
                  {isLogin ? '还没有账号？' : '已有账号？'}
                </span>
                <button
                  type="button"
                  onClick={() => {
                    setIsLogin(!isLogin);
                    setError('');
                    setSuccess('');
                  }}
                  className="ml-2 text-sm text-[var(--color-primary)] hover:underline"
                >
                  {isLogin ? '立即注册' : '立即登录'}
                </button>
              </div>
            </div>
          )}
        </form>
      </div>
    </div>
  );
}