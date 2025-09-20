# Internationalization (i18n) Documentation

## Overview

The DividaFácil application now supports internationalization, allowing for multiple languages to be easily added and maintained.

## Structure

### Translation Files
Translation files are stored in the `locales/` directory:
- `locales/pt-BR.json` - Portuguese (Brazil) - Default language
- `locales/en.json` - English

### Key Components
- `src/i18n.py` - Main internationalization service
- `src/template_engine.py` - Jinja2 integration with i18n functions
- `src/settings.py` - Configuration including default locale

## Usage in Templates

### Basic Translation
```html
<h1>{{ t('app.name') }}</h1>
<p>{{ t('dashboard.users') }}</p>
```

### Translation with Specific Locale
```html
<h1>{{ t('app.name', 'en') }}</h1>
<p>{{ t('dashboard.users', 'pt-BR') }}</p>
```

### Available Template Functions
- `t(key, locale=None, **kwargs)` - Translate a key
- `get_locale()` - Get current locale
- `get_available_locales()` - Get list of available locales

## Adding New Languages

1. Create a new JSON file in `locales/` (e.g., `locales/es.json`)
2. Copy the structure from an existing file
3. Translate all the values
4. The new language will be automatically available

Example `locales/es.json`:
```json
{
  "app": {
    "name": "DividaFácil",
    "tagline": "Divide gastos fácilmente"
  },
  "dashboard": {
    "users": "Usuarios",
    "add_user": "Agregar usuario"
  }
}
```

## Adding New Translation Keys

1. Add the key to all language files:

`locales/pt-BR.json`:
```json
{
  "new_section": {
    "welcome": "Bem-vindo!"
  }
}
```

`locales/en.json`:
```json
{
  "new_section": {
    "welcome": "Welcome!"
  }
}
```

2. Use in templates:
```html
<h1>{{ t('new_section.welcome') }}</h1>
```

## Configuration

Environment variables:
- `DEFAULT_LOCALE` - Default language (default: "pt-BR")
- `LOCALES_DIR` - Directory for translation files (default: "locales")

## Implementation Details

- Uses JSON files for translations (lightweight, no external dependencies)
- Fallback to default locale when translation not found
- Nested key support using dot notation (e.g., 'app.name')
- Automatic locale file discovery
- Template integration with Jinja2 global functions

## Testing

Run i18n tests:
```bash
python -m pytest tests/test_i18n.py -v
```

Test specific translations:
```python
from src.i18n import get_i18n_service
i18n = get_i18n_service()
print(i18n.t('app.name', 'en'))  # English
print(i18n.t('app.name', 'pt-BR'))  # Portuguese
```