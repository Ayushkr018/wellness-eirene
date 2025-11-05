from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import base64
import os
import logging

logger = logging.getLogger(__name__)

class EncryptionManager:
    """AES-256 encryption/decryption manager"""
    
    def __init__(self):
        # Get encryption key from environment (must be 32 bytes for AES-256)
        key = os.getenv('ENCRYPTION_KEY')
        if not key:
            # Generate a random key for development (use proper key management in production)
            key = base64.b64encode(os.urandom(32)).decode()
            logger.warning("Generated temporary encryption key - set ENCRYPTION_KEY in production")
        
        # Decode if base64 encoded
        try:
            self.key = base64.b64decode(key)
            if len(self.key) != 32:
                raise ValueError("Encryption key must be 32 bytes")
        except:
            # If not base64, use directly
            self.key = key.encode()[:32].ljust(32, b'0')
        
        self.backend = default_backend()
    
    def encrypt(self, plaintext):
        """Encrypt text using AES-256-CBC"""
        try:
            if not plaintext:
                return plaintext
            
            # Convert to bytes if string
            if isinstance(plaintext, str):
                plaintext = plaintext.encode('utf-8')
            
            # Generate random IV
            iv = os.urandom(16)
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(self.key),
                modes.CBC(iv),
                backend=self.backend
            )
            
            # Pad plaintext
            padder = padding.PKCS7(128).padder()
            padded_data = padder.update(plaintext) + padder.finalize()
            
            # Encrypt
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(padded_data) + encryptor.finalize()
            
            # Return IV + ciphertext (base64 encoded)
            encrypted = iv + ciphertext
            return base64.b64encode(encrypted).decode('utf-8')
            
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            return plaintext  # Return original on error (log this in production)
    
    def decrypt(self, ciphertext):
        """Decrypt text using AES-256-CBC"""
        try:
            if not ciphertext:
                return ciphertext
            
            # Decode base64
            encrypted = base64.b64decode(ciphertext)
            
            # Extract IV and ciphertext
            iv = encrypted[:16]
            ciphertext_bytes = encrypted[16:]
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(self.key),
                modes.CBC(iv),
                backend=self.backend
            )
            
            # Decrypt
            decryptor = cipher.decryptor()
            padded_data = decryptor.update(ciphertext_bytes) + decryptor.finalize()
            
            # Unpad
            unpadder = padding.PKCS7(128).unpadder()
            plaintext = unpadder.update(padded_data) + unpadder.finalize()
            
            return plaintext.decode('utf-8')
            
        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            return ciphertext  # Return original on error
    
    def encrypt_dict(self, data, fields):
        """Encrypt specific fields in a dictionary"""
        encrypted_data = data.copy()
        for field in fields:
            if field in encrypted_data and encrypted_data[field]:
                encrypted_data[field] = self.encrypt(encrypted_data[field])
                encrypted_data[f"{field}_encrypted"] = True
        return encrypted_data
    
    def decrypt_dict(self, data, fields):
        """Decrypt specific fields in a dictionary"""
        decrypted_data = data.copy()
        for field in fields:
            if field in decrypted_data and decrypted_data.get(f"{field}_encrypted"):
                decrypted_data[field] = self.decrypt(decrypted_data[field])
                del decrypted_data[f"{field}_encrypted"]
        return decrypted_data

# Global instance
encryption_manager = EncryptionManager()
