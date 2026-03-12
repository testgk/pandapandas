# Global Copilot Instructions

## Naming Conventions
- Use **camelCase** for variables, methods, and functions
- Use **PascalCase** for class names
- Use **UPPER_SNAKE_CASE** for constants

## Code Style

### Spacing
- Add space after `(`, `[`, `{` and before `)`, `]`, `}`
  ```python
  # Good
  def myMethod( self, param1, param2 ):
      myList = [ 1, 2, 3 ]
      myDict = { "key": "value" }

  # Bad
  def myMethod(self, param1, param2):
      myList = [1, 2, 3]
      myDict = {"key": "value"}
  ```

- Add space before and after `=`
  ```python
  # Good
  value = 10
  result = myFunction( arg1, arg2 )

  # Bad
  value=10
  result=myFunction(arg1, arg2)
  ```

## Avoid Anti-Patterns

### No `hasattr` or `getattr`
- Do NOT use `hasattr()` or `getattr()` for attribute access
- Use proper inheritance, abstract methods, or typed properties instead

## Type Hints
- Always use type hints for function parameters and return values
- Use typing module for complex types ( List, Dict, Optional, etc. )

## Inheritance
- Prefer composition and inheritance over duck typing
- Use abstract base classes ( ABC ) to define interfaces

## Testing Conventions

### Test Structure
Follow the three-layer test architecture:

1. **Abstract Test** ( `abstract_staged_test.py` )
2. **Scenarios** ( `*_scenarios.py` )
3. **Steps** ( `*_steps.py` )

---

## Git Workflow

### Always work on a branch
- **Never commit directly to `master`**
- Create a feature branch for every task:
  ```bash
  git checkout -b feature/my-feature-name
  ```
- Commit changes to the branch as work progresses
- Only merge to `master` when explicitly asked by the user
- Only push to `origin` when explicitly asked by the user

### Branch naming
```
feature/short-description    # new features
fix/short-description        # bug fixes
refactor/short-description   # refactoring
```

### Commit often, merge only when asked
- Commit after each logical change on the branch
- Do NOT auto-merge or auto-push after every commit
- Wait for the user to say "commit and merge" or "push" before merging/pushing

