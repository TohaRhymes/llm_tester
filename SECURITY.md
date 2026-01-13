# Security Policy

## Overview

This document outlines security measures implemented in the LLM Test Generator application and provides guidelines for secure deployment and usage.

## Security Measures Implemented

### 1. CORS Configuration (Fixed)
**Issue**: Previously used wildcard (`*`) for CORS origins
**Status**: ✅ Fixed
**Implementation**: app/main.py:31-35

- **Change**: Environment-based CORS configuration
- **Configuration**: Set `CORS_ORIGINS` environment variable
- **Default**: `http://localhost:8000,http://127.0.0.1:8000`
- **Production**: Set explicit allowed origins

```bash
# Example for production
export CORS_ORIGINS="https://yourdomain.com,https://app.yourdomain.com"
```

### 2. Path Traversal Protection (Implemented)
**Status**: ✅ Implemented
**Implementation**: app/utils/path.py:7-29

- Uses `safe_join()` utility to prevent directory traversal attacks
- Validates all file paths before file operations
- Protects upload, file retrieval, and exam retrieval endpoints

### 3. File Upload Size Limits (Fixed)
**Issue**: No size limits on file uploads
**Status**: ✅ Fixed
**Implementation**: app/api/files.py:19,50-54

- **Maximum file size**: 10MB
- **Validation**: Enforced before file is written to disk
- **Response**: HTTP 413 (Payload Too Large) for oversized files

### 4. Rate Limiting (Implemented)
**Issue**: No rate limiting on API endpoints
**Status**: ✅ Fixed
**Implementation**: app/main.py:23,36-37

- **Library**: slowapi (based on Flask-Limiter)
- **Configuration**: Applied globally via middleware
- **Default behavior**: Can be customized per endpoint

#### Applying Rate Limits to Endpoints

Add rate limits to specific endpoints:

```python
from app.main import limiter

@router.post("/api/generate")
@limiter.limit("10/minute")  # 10 requests per minute
async def generate_exam(request: Request, ...):
    pass
```

### 5. Cryptographic Hash Usage (Fixed)
**Issue**: MD5 used without `usedforsecurity=False` flag
**Status**: ✅ Fixed
**Locations**:
- app/core/exam_builder.py:139-142
- app/services/llm_provider.py:68

**Note**: MD5 is used only for non-cryptographic purposes (ID generation, seed generation). The `usedforsecurity=False` flag prevents security warnings.

### 6. Secrets Management
**Status**: ✅ Implemented

- API keys stored in `.env` file (gitignored)
- No hardcoded secrets in source code
- Uses `pydantic-settings` for environment variable management

## Deployment Security Guidelines

### Environment Variables

Required environment variables:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_key

# Yandex Configuration (if using Yandex provider)
YANDEX_CLOUD_API_KEY=your_yandex_key
YANDEX_CLOUD_API_KEY_IDENTIFIER=your_key_id
YANDEX_FOLDER_ID=your_folder_id

# CORS Configuration (production)
CORS_ORIGINS=https://yourdomain.com,https://api.yourdomain.com
```

### Production Checklist

- [ ] Set explicit CORS origins (not wildcard)
- [ ] Use HTTPS for all external communication
- [ ] Rotate API keys regularly
- [ ] Enable rate limiting on public endpoints
- [ ] Monitor file upload patterns
- [ ] Review and restrict file upload permissions
- [ ] Use reverse proxy (nginx/Caddy) with additional security headers
- [ ] Enable API authentication if needed
- [ ] Set up logging and monitoring
- [ ] Keep dependencies updated

### Additional Security Headers

When deploying behind a reverse proxy, add these headers:

```nginx
add_header X-Frame-Options "SAMEORIGIN";
add_header X-Content-Type-Options "nosniff";
add_header X-XSS-Protection "1; mode=block";
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
```

## Security Testing

### Running Security Tests

```bash
# Run security-specific unit tests
pytest tests/unit/test_security.py -v

# Run bandit security scanner
bandit -r app/ -ll

# Run safety to check dependencies
safety check
```

### Security Test Coverage

The test suite (`tests/unit/test_security.py`) covers:
- CORS configuration validation
- Path traversal prevention
- File upload size limits
- Rate limiter configuration
- MD5 usage flags
- Secrets management

## Vulnerability Reporting

If you discover a security vulnerability, please:

1. **Do NOT** open a public issue
2. Email the maintainers directly (if available)
3. Provide detailed information:
   - Vulnerability description
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

## Security Audit History

### 2026-01-13: Initial Security Audit
- Fixed CORS wildcard configuration
- Added file upload size limits (10MB)
- Implemented rate limiting with slowapi
- Fixed MD5 usage flags for bandit compliance
- Verified path traversal protection
- Created comprehensive security tests

**Bandit Scan Results**:
- Before: 2 HIGH, 1 MEDIUM, 3 LOW
- After: 0 HIGH, 1 MEDIUM, 3 LOW
- Critical issues resolved: 2
- Test coverage: 11 security tests (all passing)

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security Best Practices](https://fastapi.tiangolo.com/tutorial/security/)
- [CWE-22: Path Traversal](https://cwe.mitre.org/data/definitions/22.html)
- [CWE-327: Use of Broken Crypto](https://cwe.mitre.org/data/definitions/327.html)
- [Bandit Documentation](https://bandit.readthedocs.io/)

## License

This security policy is part of the LLM Test Generator project.
