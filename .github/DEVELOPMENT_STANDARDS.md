# Development Standards & Guidelines

## Your Role & Responsibilities
- Write clean, maintainable, and well-documented code
- Follow industry best practices and design patterns
- Implement proper error handling and validation
- Write modular, reusable components
- Consider security, performance, and scalability
- Use modern tooling and frameworks appropriately

## Code Quality Standards
- Follow SOLID principles
- Write self-documenting code with clear variable/function names
- Add comments only for complex logic or non-obvious decisions
- Implement proper separation of concerns
- Use consistent formatting and style conventions
- Include type safety where applicable
- Handle edge cases and errors gracefully
- **No emojis** - Use plain text for all output, logging, and documentation unless absolutely necessary

## Git Workflow Standards

### Branch Naming Convention
Create branches following this format: `<type>/<descriptive-name>`

**Branch Types:**
- `feature/` - New features or enhancements
- `bugfix/` - Bug fixes
- `refactor/` - Code improvements without changing functionality
- `docs/` - Documentation changes
- `test/` - Adding or updating tests
- `chore/` - Dependency updates, config changes

**Examples:**
- `feature/user-authentication`
- `feature/payment-integration`
- `bugfix/login-validation-error`
- `refactor/optimize-api-calls`

### Commit Message Standards
Follow Conventional Commits specification:

**Format:**
```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `refactor` - Code refactoring
- `docs` - Documentation changes
- `style` - Code formatting (no logic change)
- `test` - Adding/updating tests
- `perf` - Performance improvements
- `chore` - Build process, dependencies, tooling
- `ci` - CI/CD changes

**Rules:**
- Subject: Use imperative mood ("add" not "added"), lowercase, no period, max 50 characters
- Body: Explain WHAT and WHY (not HOW), wrap at 72 characters
- Footer: Reference issues when applicable (e.g., "Fixes #123")

**Examples:**
```
feat(auth): add JWT authentication middleware

Implement token-based authentication using jsonwebtoken library
with refresh token rotation for enhanced security.

Fixes #45
```
```
fix(api): resolve CORS policy error

Update CORS configuration to allow credentials and specific
origins instead of wildcard to fix authentication issues.

Closes #78
```
```
refactor(database): extract query builder into separate service

Move database query logic from controllers to dedicated service
layer for better testability and maintainability.
```

## Commit Strategy
- Make **atomic commits** - each commit should represent one logical change
- Commit frequently with meaningful messages
- Group related file changes together
- Don't mix refactoring with feature additions
- Commit working code that passes tests

## Project Structure Best Practices
- Organize files by feature or domain (not by file type)
- Use clear, consistent folder naming conventions
- Separate concerns (business logic, data access, presentation)
- Keep configuration separate and environment-aware
- Include proper .gitignore for the tech stack

## Development Workflow
For each change you make:
1. Suggest an appropriate branch name
2. Implement the feature/fix with high-quality code
3. Break changes into logical commits
4. Provide clear commit messages for each change
5. Explain your architectural decisions when relevant

## Documentation Requirements
- Create a comprehensive README.md with:
  - Project description and purpose
  - Installation instructions
  - Usage examples
  - Configuration details
  - API documentation (if applicable)
- Add inline documentation for complex functions
- Include setup instructions for development environment

## Testing Expectations
- Write unit tests for business logic
- Include integration tests for critical paths
- Aim for meaningful test coverage (not just high percentages)
- Use descriptive test names that explain the scenario

## When Creating the Project
1. Set up proper project structure from the start
2. Initialize with appropriate .gitignore, README, and config files
3. Use dependency management best practices
4. Configure linting and formatting tools
5. Set up a logical initial commit structure

## Communication
- Explain your architectural decisions
- Suggest improvements or alternatives when appropriate
- Ask clarifying questions if requirements are ambiguous
- Provide context for complex implementations

---
*These standards must be followed consistently throughout the development process. Reference this file before making any code changes.*