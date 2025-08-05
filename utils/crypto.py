# -*- coding: utf-8 -*-
"""
HSBC Little Worker - 加密解密工具
提供密码字段的加密和解密功能
"""

import base64
import hashlib
import json
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from utils.logger import logger


class CryptoManager:
    """加密管理器"""
    
    def __init__(self):
        self._salt = None
        self._key = None
        self._load_salt()
    
    def _load_salt(self):
        """从配置文件加载salt"""
        try:
            config_path = Path(__file__).parent.parent / "config" / "app_config.json"
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self._salt = config.get('salt', 'default_salt').encode('utf-8')
                    logger.debug("[CRYPTO] 🔑 Salt loaded from config")
            else:
                self._salt = b'default_salt'
                logger.warning("[CRYPTO] ⚠️ Config file not found, using default salt")
        except Exception as e:
            self._salt = b'default_salt'
            logger.error(f"[CRYPTO] ❌ Failed to load salt: {e}")
    
    def _get_key(self):
        """生成加密密钥"""
        if self._key is None:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=self._salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(b'hsbc_little_worker_key'))
            self._key = key
        return self._key
    
    def encrypt_password(self, password: str) -> str:
        """加密密码
        
        Args:
            password: 明文密码
            
        Returns:
            加密后的密码字符串
        """
        try:
            if not password:
                return ""
            
            fernet = Fernet(self._get_key())
            encrypted_bytes = fernet.encrypt(password.encode('utf-8'))
            encrypted_str = base64.urlsafe_b64encode(encrypted_bytes).decode('utf-8')
            
            logger.debug("[CRYPTO] 🔒 Password encrypted successfully")
            return encrypted_str
            
        except Exception as e:
            logger.error(f"[CRYPTO] ❌ Failed to encrypt password: {e}")
            return password  # 加密失败时返回原密码
    
    def decrypt_password(self, encrypted_password: str) -> str:
        """解密密码
        
        Args:
            encrypted_password: 加密的密码字符串
            
        Returns:
            解密后的明文密码
        """
        try:
            if not encrypted_password:
                return ""
            
            # 检查是否已经是加密格式
            if not self._is_encrypted(encrypted_password):
                return encrypted_password  # 如果不是加密格式，直接返回
            
            fernet = Fernet(self._get_key())
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_password.encode('utf-8'))
            decrypted_bytes = fernet.decrypt(encrypted_bytes)
            decrypted_str = decrypted_bytes.decode('utf-8')
            
            logger.debug("[CRYPTO] 🔓 Password decrypted successfully")
            return decrypted_str
            
        except Exception as e:
            logger.error(f"[CRYPTO] ❌ Failed to decrypt password: {e}")
            return encrypted_password  # 解密失败时返回原字符串
    
    def _is_encrypted(self, text: str) -> bool:
        """检查文本是否为加密格式
        
        Args:
            text: 要检查的文本
            
        Returns:
            True if encrypted, False otherwise
        """
        try:
            # 尝试base64解码，如果成功且长度合理，认为是加密格式
            decoded = base64.urlsafe_b64decode(text.encode('utf-8'))
            return len(decoded) > 32  # Fernet加密后的最小长度
        except Exception:
            return False


# 全局加密管理器实例
_crypto_manager = None


def get_crypto_manager() -> CryptoManager:
    """获取全局加密管理器实例"""
    global _crypto_manager
    if _crypto_manager is None:
        _crypto_manager = CryptoManager()
    return _crypto_manager


def encrypt_password(password: str) -> str:
    """加密密码的便捷函数"""
    return get_crypto_manager().encrypt_password(password)


def decrypt_password(encrypted_password: str) -> str:
    """解密密码的便捷函数"""
    return get_crypto_manager().decrypt_password(encrypted_password)


def is_password_field(field_name: str) -> bool:
    """检查字段名是否为密码字段
    
    Args:
        field_name: 字段名
        
    Returns:
        True if password field, False otherwise
    """
    return field_name.lower().startswith('password')