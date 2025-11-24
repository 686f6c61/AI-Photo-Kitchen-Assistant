# Changelog

All notable changes to the AI Photo Kitchen Assistant project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.0] - 2025-01-24

### 🚀 Added

#### OpenRouter Integration
- **Multi-Model AI Support**: Integrated OpenRouter API for access to multiple AI providers
  - Google Gemini Pro 1.5 for vision analysis
  - Anthropic Claude 3.5 Sonnet for recipe generation
  - OpenAI GPT-4/GPT-4o support
  - Meta Llama 3.1 70B support
  - Easy model switching via environment variables

#### Security Enhancements
- **Rate Limiting**: Implemented Flask-Limiter for API protection
  - Configurable per-minute and per-hour limits
  - IP-based throttling
  - Memory-backed storage for development
- **CORS Support**: Added Flask-CORS for secure cross-origin requests
- **Input Validation**: Enhanced sanitization of all user inputs
- **Secure File Handling**: Improved file type validation and cleanup

#### Code Quality
- **Professional Headers**: Added comprehensive file headers with:
  - Author information
  - Creation and update dates
  - Version numbers
  - License information
  - Detailed descriptions
- **Type Hints**: Added Python type annotations throughout codebase
- **Comprehensive Documentation**:
  - Detailed docstrings for all functions
  - Usage examples in docstrings
  - Security considerations documented
  - Performance notes included

#### Error Handling
- **Retry Logic**: Implemented exponential backoff for API calls
  - Automatic retry on transient errors
  - Configurable retry attempts (default: 3)
  - Exponential delay between retries
- **Better Error Messages**: User-friendly error responses
- **Comprehensive Logging**: Enhanced logging with emoji indicators

#### Configuration
- **Environment-based Config**: Improved configuration management
  - Automatic provider detection (OpenRouter vs OpenAI)
  - Validation on startup
  - Helpful warnings for missing configuration
- **Flexible Model Selection**: Easy model switching via environment variables

### 🔄 Changed

#### Dependencies
- Updated to specific version constraints for stability:
  - `flask>=3.0.0` (from unversioned)
  - `openai>=1.12.0` (compatible with both APIs)
  - `python-dotenv>=1.0.0`
  - Added `flask-limiter>=3.5.0`
  - Added `flask-cors>=4.0.0`
  - All dependencies pinned to minimum versions

#### Code Structure
- **Refactored `app.py`**:
  - Cleaner initialization
  - Better separation of concerns
  - Improved route documentation
  - Enhanced error handling
- **Refactored `config.py`**:
  - Multi-provider support
  - Better validation logic
  - Secure defaults
  - Auto-generated secrets for development
- **Refactored `utils.py`**:
  - Added helper functions
  - Better ingredient formatting
  - Enhanced prompt generation

#### Configuration Files
- **`.env.example`**: Completely rewritten with:
  - Detailed comments
  - OpenRouter configuration
  - Model recommendations
  - Best practices
  - All available options documented

#### Documentation
- **README.md**: Major overhaul with:
  - Version 2.0 branding
  - OpenRouter integration guide
  - Detailed installation instructions
  - Configuration examples
  - Troubleshooting section
  - Security best practices
  - Model recommendations table
  - Complete API documentation
  - Contribution guidelines

### 🔒 Security

- **Secret Management**: All secrets via environment variables
- **File Upload Security**:
  - Whitelist-based extension validation
  - Secure filename sanitization
  - Automatic cleanup of temporary files
- **Rate Limiting**: Protection against API abuse
- **Input Sanitization**: All user inputs validated and sanitized
- **Error Handling**: No sensitive information in error messages
- **CORS Configuration**: Secure cross-origin request handling

### 🐛 Fixed

- Resolved potential security issues in file upload handling
- Fixed missing error handling in API calls
- Corrected configuration validation logic
- Improved temporary file cleanup reliability

### 📖 Documentation

- Added comprehensive inline documentation
- Created professional file headers
- Documented all functions with examples
- Added security considerations to docstrings
- Included performance notes where relevant

---

## [1.0.0] - 2024-01-15

### 🎉 Initial Release

#### Features
- **Image Analysis**: GPT-4 Vision for ingredient detection
- **Recipe Generation**: AI-powered recipe creation
- **Dietary Restrictions**: Support for allergies and preferences
- **Cuisine Types**: Multiple cuisine style support
- **Web Interface**: User-friendly Flask web application
- **Shopping Lists**: Automatic generation of missing ingredients

#### Technology Stack
- Flask web framework
- OpenAI API integration
- Bootstrap 5 frontend
- Python-dotenv for configuration

#### Basic Functionality
- Upload refrigerator photos
- Detect ingredients from images
- Generate personalized recipes
- Copy recipes to clipboard
- Mobile-responsive design

---

## Migration Guide: v1.0 → v2.0

### Required Changes

1. **Update Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Update `.env` File**:
   ```bash
   # Add OpenRouter support (optional but recommended)
   OPENROUTER_API_KEY=your-key-here
   OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

   # Update model names if using OpenRouter
   IMAGE_MODEL=google/gemini-pro-1.5-exp
   RECIPE_MODEL=anthropic/claude-3.5-sonnet

   # Add rate limiting (optional)
   RATE_LIMIT_PER_MINUTE=10
   RATE_LIMIT_PER_HOUR=50
   ```

3. **Update Python Version** (if needed):
   - v1.0: Python 3.8+
   - v2.0: Python 3.9+ (recommended 3.11+)

### Breaking Changes

- None! v2.0 is backward compatible with v1.0 configuration
- Existing OpenAI API keys continue to work
- All v1.0 features remain functional

### New Features Available

- Switch to OpenRouter for multi-model support
- Enable rate limiting for production use
- Use new logging configuration
- Leverage improved error handling

---

## Upcoming Features

### Planned for v2.1
- [ ] Redis-backed caching for repeated requests
- [ ] Recipe history and favorites
- [ ] Export recipes to PDF
- [ ] Multi-language support (i18n)
- [ ] User accounts and preferences

### Planned for v2.2
- [ ] Docker containerization
- [ ] Unit and integration tests
- [ ] CI/CD with GitHub Actions
- [ ] Database integration (PostgreSQL/SQLite)
- [ ] RESTful API endpoints

### Planned for v3.0
- [ ] Real-time updates with WebSockets
- [ ] Image quality enhancement
- [ ] Nutrition calculation improvements
- [ ] Mobile app (React Native)
- [ ] Community recipe sharing

---

## Contributors

- **686f6c61** - *Initial work and v2.0 refactor* - [GitHub](https://github.com/686f6c61)

---

## Links

- **Repository**: https://github.com/686f6c61/AI-Photo-Kitchen-Assistant
- **Issues**: https://github.com/686f6c61/AI-Photo-Kitchen-Assistant/issues
- **Pull Requests**: https://github.com/686f6c61/AI-Photo-Kitchen-Assistant/pulls

---

*For more information, see the [README](README.md)*
