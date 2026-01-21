# Contributing to LLM Test Generator

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Code Style](#code-style)
- [Commit Messages](#commit-messages)
- [Pull Requests](#pull-requests)
- [Issue Reporting](#issue-reporting)

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Keep discussions professional

## Getting Started

### Prerequisites

- Python 3.11+
- pip
- Git
- OpenAI API key (or use local stub mode)

### Setup Development Environment

1. **Fork and clone**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/llm_tester.git
   cd llm_tester
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   # Or use DEFAULT_PROVIDER=local for testing without API key
   ```

4. **Run tests**:
   ```bash
   pytest tests/unit/ -v
   ```

5. **Start development server**:
   ```bash
   uvicorn app.main:app --reload
   ```

## Development Workflow

We follow **Test-Driven Development (TDD)** and track all work through **GitHub Issues**.

### TDD Workflow

1. **Write failing tests first** (RED phase)
2. **Write minimal code to pass tests** (GREEN phase)
3. **Refactor** while keeping tests green

Example:
```python
# 1. RED - Write failing test
def test_new_feature():
    result = my_new_function()
    assert result == expected_value

# 2. GREEN - Implement minimal code
def my_new_function():
    return expected_value

# 3. REFACTOR - Improve while tests pass
def my_new_function():
    # Better implementation
    return compute_expected_value()
```

### Issue-Driven Development

1. **Check existing issues** or create a new one
2. **Reference issue in commits**: `feat: add feature (issue #123)`
3. **Close issues via commits**: `fix: resolve bug - Closes #123`
4. **Small, atomic commits** - one logical change per commit

## Testing

### Test Structure

```
tests/
├── unit/           # Unit tests (TDD)
├── integration/    # Integration tests
└── bdd/            # Behavior-Driven Development tests
    ├── features/   # Gherkin .feature files
    └── steps/      # Step definitions
```

### Running Tests

```bash
# All unit tests
pytest tests/unit/ -v

# Specific test file
pytest tests/unit/test_generator.py -v

# With coverage
pytest --cov=app --cov-report=html tests/

# BDD tests
behave tests/bdd/features/

# Security scan
bandit -r app/ -ll
```

### Test Coverage Requirements

- **Minimum**: 80% code coverage
- **All new features**: Must have tests
- **All bug fixes**: Must have regression tests

### Writing Tests

```python
# Unit test example
def test_question_generator():
    """Test question generation with specific config."""
    generator = QuestionGenerator()
    document = parser.parse("# Test\nContent here")

    config = ExamConfig(
        total_questions=5,
        single_choice_ratio=1.0
    )

    exam = generator.generate(document, config, "test-exam")

    assert len(exam.questions) == 5
    assert all(q.type == "single_choice" for q in exam.questions)
```

## Code Style

### Python

- **Style Guide**: PEP 8
- **Line Length**: 100 characters (not strict 79)
- **Imports**: Organized (stdlib, third-party, local)
- **Type Hints**: Use when it improves clarity
- **Docstrings**: Google style for functions/classes

Example:
```python
from typing import List, Optional
from pydantic import BaseModel

def generate_questions(
    content: str,
    count: int,
    difficulty: str = "medium"
) -> List[Question]:
    """
    Generate questions from content.

    Args:
        content: Source markdown content
        count: Number of questions to generate
        difficulty: Question difficulty level

    Returns:
        List of generated Question objects

    Raises:
        ValueError: If count is invalid
    """
    if count <= 0:
        raise ValueError("Count must be positive")

    # Implementation
    return questions
```

### JavaScript

- **Style**: Modern ES6+
- **Modules**: Use module pattern with window exports
- **Naming**: camelCase for functions/variables
- **Documentation**: JSDoc comments for public functions
- **Error Handling**: Always use try-catch for async

Example:
```javascript
/**
 * Upload file with validation
 * @param {File} file - File to upload
 * @returns {Promise<Object>} Upload result
 */
async function uploadFile(file) {
    // Validate
    const validation = UIUtils.validateFile(file);
    if (!validation.valid) {
        throw new Error(validation.error);
    }

    // Upload
    try {
        const result = await API.uploadFile(file);
        return result;
    } catch (error) {
        console.error('Upload failed:', error);
        throw error;
    }
}
```

## Commit Messages

### Format

```
<type>(<scope>): <subject> (issue #N)

<body>

<footer>
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **security**: Security fixes
- **perf**: Performance improvements
- **chore**: Maintenance tasks

### Examples

```bash
# Feature
git commit -m "feat(frontend): add file delete button (issue #20)

Added delete functionality for uploaded files with confirmation dialog.

Closes #20"

# Bug fix
git commit -m "fix(grader): correct partial credit calculation (issue #21)

Fixed bug where multiple choice questions with 3+ correct answers
received incorrect partial credit scores.

Fixes #21"

# Documentation
git commit -m "docs: update README with new frontend architecture

Added frontend architecture section linking to docs/ARCHITECTURE.md.
Updated installation instructions."

# Security
git commit -m "security: add input sanitization for markdown content

Sanitize user-provided markdown to prevent XSS attacks.

Related to security audit."
```

### Commit Best Practices

- **Atomic commits**: One logical change per commit
- **Present tense**: "add feature" not "added feature"
- **Descriptive**: Explain what and why, not how
- **Reference issues**: Always link to issue number
- **Sign commits**: Use Co-Authored-By for pair programming

## Pull Requests

### Before Creating PR

1. ✅ All tests pass
2. ✅ Code coverage maintained/improved
3. ✅ Documentation updated
4. ✅ Commits are clean and atomic
5. ✅ Branch is up to date with main

### PR Template

```markdown
## Description
Brief description of changes

## Related Issue
Closes #N

## Changes Made
- Change 1
- Change 2

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Tests pass
- [ ] Coverage ≥ 80%
- [ ] Documentation updated
- [ ] Commit messages follow convention
```

### Review Process

1. **Automated checks** must pass (tests, coverage, security)
2. **Code review** by maintainer
3. **Requested changes** addressed
4. **Approved** → Merged to main

## Issue Reporting

### Bug Reports

```markdown
**Bug Description**
Clear description of the bug

**Steps to Reproduce**
1. Step 1
2. Step 2
3. See error

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- OS:
- Python version:
- Browser (if frontend):

**Additional Context**
Screenshots, logs, etc.
```

### Feature Requests

```markdown
**Feature Description**
What feature do you want?

**Use Case**
Why is this feature needed?

**Proposed Solution**
How might this work?

**Alternatives**
Other approaches considered?
```

## Project Structure

See `README.md` for the canonical tree and `docs/ARCHITECTURE.md` for component-level details.

## Security

### Reporting Security Issues

**DO NOT** open public issues for security vulnerabilities.

Instead:
1. Email maintainers (if contact available)
2. Provide detailed vulnerability report
3. Allow time for fix before public disclosure

See [SECURITY.md](SECURITY.md) for more details.

### Security Best Practices

- **Never commit secrets** (.env in .gitignore)
- **Validate all inputs** (client and server)
- **Sanitize user content**
- **Use prepared statements** for database queries
- **Keep dependencies updated**
- **Run security scans** (bandit, safety)

## Documentation

### When to Update Docs

- **New features**: Document in README or separate doc
- **API changes**: Update OpenAPI/Swagger
- **Breaking changes**: Update CHANGELOG.md
- **Architecture changes**: Update relevant docs

### Documentation Files

Start with `README.md`, then use `docs/ARCHITECTURE.md` (architecture + API + frontend),
`docs/PLAN.md` (roadmap), `docs/SECURITY.md` (security policy), and
`docs/CHANGELOG.md` (history).

## Getting Help

- **Documentation**: Start with README.md
- **Issues**: Search existing issues
- **Discussions**: GitHub Discussions (if enabled)
- **Code**: Read existing code and tests

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

## Quick Reference

```bash
# Setup
pip install -r requirements.txt
cp .env.example .env

# Development
uvicorn app.main:app --reload

# Testing
pytest tests/unit/ -v                    # Unit tests
pytest --cov=app tests/                  # With coverage
behave tests/bdd/features/               # BDD tests
bandit -r app/ -ll                       # Security scan

# Git workflow
git checkout -b feature/my-feature
# Make changes, write tests
pytest tests/unit/ -v
git add .
git commit -m "feat: add feature (issue #N)"
git push origin feature/my-feature
# Create PR on GitHub
```

---

**Thank you for contributing!** 🎉
