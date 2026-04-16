"""邮件发送服务"""

import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from loguru import logger

from config.settings import settings


class EmailService:
    """邮件服务"""
    
    def __init__(self):
        # 使用126邮箱配置
        self.smtp_host = "smtp.126.com"
        self.smtp_port = 465  # 465 (SSL) 是126邮箱推荐的端口
        self.sender_email = "Tagent_official@126.com"
        # 注意：126邮箱需要使用"客户端授权密码"而非邮箱密码
        # 获取方式：登录126邮箱 → 设置 → POP3/SMTP/IMAP → 开启服务 → 设置客户端授权密码
        self.sender_password = "XGenHwPA6JC43tab"  # 126邮箱的客户端授权密码
        self.sender_name = "Tagent_official"
        
        # 开发模式控制：True=模拟发送(控制台输出), False=真实发送邮件
        # 现在已经有了授权码，可以启用真实邮件发送
        # 已启用生产模式，可以发送真实邮件
        self.development_mode = False  # 生产模式：发送真实邮件
    
    def send_password_reset_email(self, to_email: str, reset_code: str) -> bool:
        """发送密码重置邮件"""
        # 开发模式：模拟邮件发送
        if self.development_mode:
            logger.info(f"[开发模式] 模拟发送密码重置邮件到 {to_email}")
            logger.info(f"[开发模式] 重置验证码: {reset_code}")
            print(f"=== 开发模式邮件 ===")
            print(f"收件人: {to_email}")
            print(f"验证码: {reset_code}")
            print(f"有效期: 10分钟")
            print(f"==================")
            return True
        
        try:
            # 创建邮件内容
            subject = "Tagent 密码重置验证码"
            
            html_content = f"""
            <html>
            <body>
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; font-family: Arial, sans-serif;">
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 30px;">
                        <h1 style="color: white; margin: 0; font-size: 28px;">🔐 密码重置</h1>
                        <p style="color: #f0f0f0; margin: 10px 0 0 0; font-size: 16px;">Tagent 知识库智能助手</p>
                    </div>
                    
                    <div style="background: #f8f9fa; padding: 25px; border-radius: 8px; margin-bottom: 25px;">
                        <h2 style="color: #333; margin-top: 0;">您好！</h2>
                        <p style="color: #555; line-height: 1.6; font-size: 16px;">
                            我们收到了您的密码重置请求。请使用下面的验证码来重置您的密码：
                        </p>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <div style="display: inline-block; background: #007bff; color: white; padding: 15px 30px; border-radius: 6px; font-size: 24px; font-weight: bold; letter-spacing: 3px;">
                                {reset_code}
                            </div>
                        </div>
                        
                        <p style="color: #666; font-size: 14px; margin-bottom: 0;">
                            ⚠️ 验证码将在 <strong>10分钟</strong> 后过期，请尽快使用。
                        </p>
                    </div>
                    
                    <div style="border-left: 4px solid #28a745; padding: 15px 20px; background: #f8fff9; margin-bottom: 25px;">
                        <p style="color: #155724; margin: 0; font-size: 14px;">
                            <strong>安全提醒：</strong>如果您没有申请密码重置，请忽略此邮件。为了账户安全，请不要将验证码告诉任何人。
                        </p>
                    </div>
                    
                    <div style="text-align: center; padding: 20px; border-top: 1px solid #eee; color: #888; font-size: 14px;">
                        <p style="margin: 5px 0;">此邮件由 Tagent 智能助手自动发送</p>
                        <p style="margin: 5px 0;">如需帮助，请联系我们的技术支持</p>
                        <p style="margin: 15px 0 5px 0; font-weight: bold;">—— Tagent_official</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # 创建邮件
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.sender_name} <{self.sender_email}>"
            msg['To'] = to_email
            
            # 添加HTML内容
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # 发送邮件 - 使用SSL连接（端口465）
            with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port) as server:
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            logger.info(f"密码重置邮件已发送到: {to_email}")
            return True
            
        except Exception as e:
            error_msg = str(e)
            if "550" in error_msg:
                logger.error(f"邮件发送失败 - 认证错误: {e}")
                logger.error("提示：126邮箱需要使用客户端授权密码，不是邮箱登录密码")
            elif "Connection" in error_msg:
                logger.error(f"邮件发送失败 - 连接错误: {e}")
                logger.error("提示：检查SMTP服务器设置和网络连接")
            else:
                logger.error(f"邮件发送失败: {e}")
            return False
    
    def send_welcome_email(self, to_email: str, nickname: str) -> bool:
        """发送欢迎邮件"""
        # 开发模式：模拟邮件发送
        if self.development_mode:
            logger.info(f"[开发模式] 模拟发送欢迎邮件到 {to_email}")
            print(f"=== 欢迎邮件 ===")
            print(f"Hi {nickname}! 欢迎使用 Tagent 智能助手!")
            print(f"===============")
            return True
        
        try:
            subject = "欢迎使用 Tagent 智能助手！"
            
            html_content = f"""
            <html>
            <body>
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; font-family: Arial, sans-serif;">
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 30px;">
                        <h1 style="color: white; margin: 0; font-size: 28px;">🎉 欢迎加入 Tagent！</h1>
                        <p style="color: #f0f0f0; margin: 10px 0 0 0; font-size: 16px;">您的智能知识库助手</p>
                    </div>
                    
                    <div style="padding: 25px;">
                        <h2 style="color: #333;">Hi {nickname}！</h2>
                        <p style="color: #555; line-height: 1.6; font-size: 16px;">
                            恭喜您成功注册 Tagent 智能助手！🎊 欢迎加入我们的智能知识库社区。
                        </p>
                        
                        <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                            <h3 style="color: #007bff; margin-top: 0;">✨ 您可以开始：</h3>
                            <ul style="color: #555; line-height: 1.8;">
                                <li>🤖 与AI助手进行智能对话</li>
                                <li>📚 搜索知识库获取准确答案</li>
                                <li>💾 保存重要对话记录</li>
                                <li>📌 置顶常用对话内容</li>
                                <li>🔄 创建新的对话会话</li>
                            </ul>
                        </div>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="#" style="display: inline-block; background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">
                                立即开始体验
                            </a>
                        </div>
                    </div>
                    
                    <div style="text-align: center; padding: 20px; border-top: 1px solid #eee; color: #888; font-size: 14px;">
                        <p style="margin: 5px 0;">感谢您选择 Tagent 智能助手</p>
                        <p style="margin: 15px 0 5px 0; font-weight: bold;">—— Tagent_official</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # 创建邮件
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.sender_name} <{self.sender_email}>"
            msg['To'] = to_email
            
            # 添加HTML内容
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # 发送邮件 - 使用SSL连接（端口465）
            with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port) as server:
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            logger.info(f"欢迎邮件已发送到: {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"发送欢迎邮件失败: {e}")
            return False

    def send_registration_verification_email(self, to_email: str, verification_code: str) -> bool:
        """发送注册验证邮件"""
        # 开发模式：模拟邮件发送
        if self.development_mode:
            logger.info(f"[开发模式] 模拟发送注册验证邮件到 {to_email}")
            logger.info(f"[开发模式] 注册验证码: {verification_code}")
            print(f"=== 开发模式邮件 ===")
            print(f"收件人: {to_email}")
            print(f"验证码: {verification_code}")
            print(f"有效期: 10分钟")
            print(f"==================")
            return True
        
        try:
            # 创建邮件内容
            subject = "Tagent 注册验证码"
            
            html_content = f"""
            <html>
            <body>
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; font-family: Arial, sans-serif;">
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 30px;">
                        <h1 style="color: white; margin: 0; font-size: 28px;">📧 注册验证</h1>
                        <p style="color: #f0f0f0; margin: 10px 0 0 0; font-size: 16px;">Tagent 知识库智能助手</p>
                    </div>
                    
                    <div style="background: #f8f9fa; padding: 25px; border-radius: 8px; margin-bottom: 25px;">
                        <h2 style="color: #333; margin-top: 0;">欢迎注册 Tagent！</h2>
                        <p style="color: #555; line-height: 1.6; font-size: 16px;">
                            为了确保邮箱地址的有效性，请使用以下验证码完成注册：
                        </p>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <div style="display: inline-block; background: #28a745; color: white; padding: 15px 30px; border-radius: 6px; font-size: 24px; font-weight: bold; letter-spacing: 3px;">
                                {verification_code}
                            </div>
                        </div>
                        
                        <p style="color: #666; font-size: 14px; margin-bottom: 0;">
                            ⚠️ 验证码将在 <strong>10分钟</strong> 后过期，请尽快使用。
                        </p>
                    </div>
                    
                    <div style="border-left: 4px solid #17a2b8; padding: 15px 20px; background: #f0f9ff; margin-bottom: 25px;">
                        <p style="color: #0c5460; margin: 0; font-size: 14px;">
                            <strong>注意：</strong>如果您没有申请注册，请忽略此邮件。为了账户安全，请不要将验证码告诉任何人。
                        </p>
                    </div>
                    
                    <div style="text-align: center; padding: 20px; border-top: 1px solid #eee; color: #888; font-size: 14px;">
                        <p style="margin: 5px 0;">此邮件由 Tagent 智能助手自动发送</p>
                        <p style="margin: 5px 0;">如需帮助，请联系我们的技术支持</p>
                        <p style="margin: 15px 0 5px 0; font-weight: bold;">—— Tagent_official</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # 创建邮件
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.sender_name} <{self.sender_email}>"
            msg['To'] = to_email
            
            # 添加HTML内容
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # 发送邮件 - 使用SSL连接（端口465）
            with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port) as server:
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            logger.info(f"注册验证邮件已发送到: {to_email}")
            return True
            
        except Exception as e:
            error_msg = str(e)
            if "550" in error_msg:
                logger.error(f"邮件发送失败 - 认证错误: {e}")
                logger.error("提示：126邮箱需要使用客户端授权密码，不是邮箱登录密码")
            elif "Connection" in error_msg:
                logger.error(f"邮件发送失败 - 连接错误: {e}")
                logger.error("提示：检查SMTP服务器设置和网络连接")
            else:
                logger.error(f"发送注册验证邮件失败: {e}")
            return False