import pytest
from src.i18n import get_i18n_service, I18nService


def test_i18n_service_basic_functionality():
    """Test basic i18n service functionality."""
    i18n = get_i18n_service()
    
    # Test available locales
    locales = i18n.get_available_locales()
    assert 'pt-BR' in locales
    assert 'en' in locales
    
    # Test Portuguese translations
    assert i18n.t('app.name', 'pt-BR') == 'DividaFácil'
    assert i18n.t('dashboard.users', 'pt-BR') == 'Usuários'
    assert i18n.t('dashboard.add_user', 'pt-BR') == 'Adicionar usuário'
    
    # Test English translations
    assert i18n.t('app.name', 'en') == 'DividaFácil'
    assert i18n.t('dashboard.users', 'en') == 'Users'
    assert i18n.t('dashboard.add_user', 'en') == 'Add user'


def test_i18n_fallback_to_default_locale():
    """Test fallback behavior when translation not found."""
    i18n = get_i18n_service()
    
    # Test missing key fallback
    assert i18n.t('missing.key', 'pt-BR') == 'missing.key'
    assert i18n.t('missing.key', 'en') == 'missing.key'
    
    # Test fallback to default locale
    # If a key doesn't exist in English, it should fallback to Portuguese
    result = i18n.t('app.name', 'non-existent-locale')
    assert result == 'DividaFácil'  # Should fallback to default locale


def test_i18n_service_with_custom_default():
    """Test i18n service with custom default locale."""
    # Create a new instance with English as default
    i18n = I18nService(default_locale='en')
    
    # Without specifying locale, should use English
    assert i18n.t('dashboard.users') == 'Users'
    assert i18n.t('dashboard.add_user') == 'Add user'


def test_i18n_string_formatting():
    """Test string formatting functionality."""
    i18n = get_i18n_service()
    
    # Add a test translation with formatting (we can add this to test files if needed)
    # For now, test that the formatting mechanism works even if the translation doesn't have placeholders
    result = i18n.t('app.name', 'pt-BR', test_var='test')
    assert result == 'DividaFácil'  # Should not break even with extra kwargs