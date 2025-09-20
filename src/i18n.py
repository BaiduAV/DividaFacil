import json
import os
from functools import lru_cache
from typing import Dict, Any, Optional
from pathlib import Path


class I18nService:
    """Simple internationalization service for template translations."""
    
    def __init__(self, locales_dir: str = "locales", default_locale: str = "pt-BR"):
        self.locales_dir = Path(locales_dir)
        self.default_locale = default_locale
        self._translations: Dict[str, Dict[str, Any]] = {}
        self._load_translations()
    
    def _load_translations(self):
        """Load all translation files from the locales directory."""
        if not self.locales_dir.exists():
            return
            
        for json_file in self.locales_dir.glob("*.json"):
            locale = json_file.stem
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    self._translations[locale] = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"Warning: Could not load translation file {json_file}: {e}")
    
    def get_translation(self, key: str, locale: Optional[str] = None, default: Optional[str] = None) -> str:
        """
        Get a translation for the given key and locale.
        
        Args:
            key: Dot-separated key (e.g., 'app.name', 'dashboard.users')
            locale: Target locale (defaults to default_locale)
            default: Default value if translation not found
            
        Returns:
            Translated string or default value
        """
        if locale is None:
            locale = self.default_locale
            
        translations = self._translations.get(locale, {})
        
        # Navigate through nested dictionary using dot notation
        keys = key.split('.')
        value = translations
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                # Fallback to default locale if current locale doesn't have the key
                if locale != self.default_locale:
                    return self.get_translation(key, self.default_locale, default)
                return default or key
        
        return str(value) if value is not None else (default or key)
    
    def get_available_locales(self) -> list[str]:
        """Get list of available locales."""
        return list(self._translations.keys())
    
    def t(self, key: str, locale: Optional[str] = None, **kwargs) -> str:
        """
        Convenient alias for get_translation with string formatting support.
        
        Args:
            key: Translation key
            locale: Target locale
            **kwargs: Variables for string formatting
            
        Returns:
            Formatted translated string
        """
        translation = self.get_translation(key, locale)
        
        if kwargs:
            try:
                return translation.format(**kwargs)
            except (KeyError, ValueError):
                return translation
                
        return translation


# Global instance for easy access
@lru_cache(maxsize=1)
def get_i18n_service() -> I18nService:
    """Get the global i18n service instance."""
    return I18nService()