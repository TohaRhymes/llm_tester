# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive frontend architecture documentation (docs/ARCHITECTURE.md)
- Project audit report (AUDIT_REPORT.md)
- Security policy documentation (SECURITY.md)

### Changed
- Frontend completely refactored to modular architecture
- HTML reduced from 879 to 170 lines (-81%)
- All JavaScript extracted to 6 modules (953 lines)
- All CSS extracted to external stylesheet (225 lines)

## [0.2.0] - 2026-01-13

### Added
- Modular JavaScript architecture
  - api-client.js - Centralized API communication
  - ui-utils.js - UI helpers and validation
  - file-manager.js - File operations
  - exam-manager.js - Exam management
  - test-taker.js - Test taking and grading
  - main.js - Application initialization
- Professional error handling with APIError class
- User-friendly error messages
- Input validation (files, configs)
- Loading states with spinners
- Security audit with comprehensive fixes
- Rate limiting support with slowapi
- File upload size limits (10MB)
- Environment-based CORS configuration
- Security test suite (11 tests)
- SECURITY.md documentation
- AUDIT_REPORT.md project audit

### Changed
- Frontend architecture completely refactored
- CSS extracted to external file
- JavaScript modularized into 6 files
- Error handling improved across all modules
- No more alert() calls in frontend
- Better user feedback messages

### Fixed
- CORS wildcard vulnerability → environment-based origins
- Missing file upload size limits → 10MB limit enforced
- MD5 usage flags → usedforsecurity=False added
- Path traversal protection verified and tested
- Silent error failures → visible user feedback
- Code duplication eliminated

### Security
- Fixed CORS wildcard configuration (HIGH)
- Added file upload size limits (HIGH)
- Implemented rate limiting (HIGH)
- Fixed MD5 security flags (MEDIUM)
- Verified path traversal protection
- Bandit scan: 2 HIGH → 0 HIGH critical issues

**Commits**:
- a07f865: docs: create frontend architecture documentation
- 8524db5: refactor(frontend): complete modularization
- 3d76bbf: feat(frontend): create API client and utilities
- d93355e: refactor(frontend): extract CSS to separate file
- a4e4066: security: comprehensive security audit and fixes

**Issues Closed**: #9 (Frontend refactoring), #10 (Security audit)

## [0.1.0] - Previous Version

### Added
- Initial FastAPI implementation
- Markdown parsing and chunking
- Question generation (single-choice, multiple-choice, open-ended)
- Answer grading with partial credit
- OpenAI GPT integration
- YandexGPT integration
- Model answer evaluation system
- Web UI for exam generation and taking
- File upload API
- Exam management API
- Health check endpoint
- Swagger/OpenAPI documentation
- Docker and Docker Compose support
- Unit tests and BDD tests
- Language selection (English/Russian)

### Features
- Generate exams from Markdown content
- Single-choice questions
- Multiple-choice questions with partial credit
- Open-ended questions with AI grading
- Provider-agnostic LLM interface
- Model comparison and evaluation
- Jupyter-friendly examples
- Postman collection for API testing

**Issues Implemented**: #1-#8, #11-#16

---

## Version History Summary

- **0.2.0** (2026-01-13): Frontend refactoring + Security audit
- **0.1.0** (Previous): Initial implementation with core features

## Migration Guide

### Upgrading from 0.1.0 to 0.2.0

**Frontend Changes**:
- No breaking changes for API users
- Frontend completely redesigned but functionality unchanged
- If you customized static/index.html, you'll need to adapt to new modular structure

**Security Changes**:
- Set `CORS_ORIGINS` environment variable for production (was wildcard before)
- File uploads now limited to 10MB (was unlimited)
- Rate limiting available (configure per endpoint if needed)

**Configuration**:
```bash
# Add to .env for production
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

**No Database Migrations**: File-based storage unchanged

---

## Links

- [Frontend Architecture](docs/ARCHITECTURE.md)
- [Security Policy](SECURITY.md)
- [Project Audit](AUDIT_REPORT.md)
- [Development Guidelines](CLAUDE.md)
- [GitHub Repository](https://github.com/TohaRhymes/llm_tester)
