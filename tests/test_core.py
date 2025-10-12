"""
Unit tests for core utilities and functions.
"""
import pytest
from datetime import datetime, timedelta
from src.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    verify_token,
)
from src.utils.logger import get_logger, setup_logging
from src.utils.performance import timed, async_timed

def test_password_hashing():
    """Test password hashing and verification."""
    password = "test_password_123"
    hashed = get_password_hash(password)
    
    # Verify correct password
    assert verify_password(password, hashed) is True
    
    # Verify incorrect password
    assert verify_password("wrong_password", hashed) is False

def test_jwt_token_creation_and_verification():
    """Test JWT token creation and verification."""
    data = {"sub": "test_user"}
    token = create_access_token(data)
    
    # Verify token
    user = verify_token(token)
    assert user == "test_user"

def test_jwt_token_expiration():
    """Test JWT token expiration."""
    data = {"sub": "test_user"}
    expires_delta = timedelta(seconds=-1)  # Already expired
    token = create_access_token(data, expires_delta)
    
    # Token should be invalid due to expiration
    user = verify_token(token)
    assert user is None

def test_invalid_jwt_token():
    """Test invalid JWT token."""
    invalid_token = "invalid.token.string"
    user = verify_token(invalid_token)
    assert user is None

def test_logger_initialization():
    """Test logger initialization."""
    setup_logging("DEBUG")
    logger = get_logger("test")
    
    # Logger should be callable
    assert logger is not None
    logger.info("Test log message")

def test_timed_decorator():
    """Test the timed decorator."""
    @timed
    def sample_function():
        return "result"
    
    result = sample_function()
    assert result == "result"

@pytest.mark.asyncio
async def test_async_timed_decorator():
    """Test the async_timed decorator."""
    @async_timed
    async def sample_async_function():
        return "async_result"
    
    result = await sample_async_function()
    assert result == "async_result"

def test_password_hash_uniqueness():
    """Test that same password generates different hashes."""
    password = "same_password"
    hash1 = get_password_hash(password)
    hash2 = get_password_hash(password)
    
    # Hashes should be different due to salting
    assert hash1 != hash2
    
    # But both should verify correctly
    assert verify_password(password, hash1) is True
    assert verify_password(password, hash2) is True
