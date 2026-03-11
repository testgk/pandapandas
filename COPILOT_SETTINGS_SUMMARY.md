# GitHub Copilot Settings and Configuration Summary

## Date: March 11, 2026

## Project Context
- **Project**: GeoPandas Globe Application with Panda3D
- **Location**: D:\geopandas
- **Current Branch**: feature/new-development
- **Main Application**: p3d/globe_app.py

## Development Environment
- **OS**: Windows
- **Shell**: PowerShell v5.1
- **Python**: Virtual environment at p3d/venv/
- **Framework**: Panda3D for 3D graphics
- **Data**: GeoPandas for geographic data processing

## Copilot Behavior Settings

### Code Style Preferences
- **Naming Convention**: camelCase for methods and variables
- **Field Encapsulation**: Private fields with `__` prefix (double underscore)
- **Method Visibility**: Private methods with `__` prefix
- **Type Hints**: Comprehensive typing throughout codebase
- **Magic Numbers**: Eliminated and replaced with constants or settings
- **Code Formatting**: Spaces after opening brackets ( [ { and before closing brackets ) ] }
- **Assignment Spacing**: Spaces before and after equals sign (variable = value)
- **Import Ordering**: Order imports from shortest to longest line
- **Import Grouping**: Standard library → Third-party → Local imports with blank line separation
- **Attribute Access**: Avoid getattr()/hasattr(), use direct access or try/except instead
- **Pyramid of Doom**: Avoid deep nesting (max 2 levels), use early returns and guard clauses
- **Exception Handling**: Use try-except with custom exception classes, avoid generic Exception catching
- **Code Structure**: Prefer early returns, flat conditional structure, guard clauses at function start

### Workflow Preferences
- **Branch Management**: Always work on side branches, never directly on master
- **Feature Branches**: Auto-create feature branches for new development
- **Branch Naming**: Use descriptive names with prefixes (feature/, bugfix/, refactor/)
- **Commit Strategy**: Frequent commits with descriptive messages, one commit per working subject
- **Merge Process**: Never merge without permission, always get approval first
- **Post-Merge**: Update master and create new branch immediately after merge
- **Testing**: Always test before merging to master
- **History Management**: Maintain clean git history

### Architecture Patterns
- **Interface-Based Design**: Abstract base classes with IGlobeApplication interface
- **Separation of Concerns**: GUI, business logic, and data management separated
- **Settings Management**: JSON-based configuration system
- **Error Handling**: Graceful fallbacks and proper exception handling

### File Organization
```
p3d/
├── globe_app.py              # Main application
├── world_data_manager.py     # Data management
├── gui/                      # GUI components
│   └── globe_gui_controller.py
├── interfaces/               # Abstract interfaces
│   └── i_globe_application.py
├── settings/                 # Configuration system
│   ├── gui_settings.json
│   └── gui_settings_manager.py
└── tests/                    # Test files (excluded from refactoring)
```

### Code Quality Standards
- **Type Safety**: All methods have proper type hints
- **Encapsulation**: Private implementation details hidden
- **Configuration**: External JSON settings for colors, layout, text
- **Documentation**: Clear docstrings and comments
- **Error Resilience**: Fallback values and graceful error handling

### Refactoring Patterns Applied
1. **Protected to Private**: `_field` → `__field`
2. **Snake to Camel Case**: `method_name()` → `methodName()`
3. **Magic Number Elimination**: Hardcoded values → settings-based
4. **Type Addition**: Untyped → properly typed with return types
5. **Interface Implementation**: Concrete classes → interface compliance

### Git Workflow
- **Main Branch**: master (protected, no direct commits)
- **Development Branch**: Always use feature branches from master
- **Branch Naming**: feature/{description}, bugfix/{description}, refactor/{description}
- **Commit Style**: Detailed commits with clear feature descriptions, one per working subject
- **Merge Strategy**: Feature branches merged to master ONLY with permission
- **Merge Workflow**: Get permission → Test → Merge → Update master → Create new branch
- **Safety Rule**: Never work directly on master branch
- **Auto-Creation**: Automatically create feature branches for new development
- **Post-Merge Process**: Always update master and create new branch after successful merge

### Testing Approach
- **Test Files**: Preserved in tests/ directory
- **Test Methods**: Kept in snake_case (not converted to camelCase)
- **Test Organization**: Separated from main codebase

### Dependencies and Libraries
- **Core**: Panda3D for 3D graphics and GUI
- **Data**: GeoPandas for geographic data processing
- **Geometry**: Shapely for geometric operations
- **HTTP**: Requests with SSL bypass for data downloading
- **JSON**: Built-in json module for settings management
- **Typing**: Comprehensive use of typing module

### Performance Considerations
- **Caching**: World data cached locally to avoid repeated downloads
- **SSL Bypass**: Configured for certificate issues with data sources
- **Memory Management**: Proper cleanup and resource management
- **Task Management**: Panda3D task manager for async operations

### Configuration Files
- **GUI Settings**: settings/gui_settings.json
- **Colors**: Configurable button and text colors
- **Layout**: Configurable positions and scales
- **Effects**: Configurable timing and behavior
- **Content**: Configurable text labels and messages
- **Code Formatting**: Configurable spacing preferences for brackets and operators
- **Workflow Preferences**: Git branch management and development workflow settings
- **Code Style Rules**: Import ordering, attribute access patterns, violation detection
- **Git Ignore**: Comprehensive .gitignore for Python, Panda3D, and project files

### Known Issues and Solutions
- **SSL Certificates**: Bypassed using ssl._create_unverified_context
- **Data Loading**: Multiple fallback URLs for geographic data
- **Task Manager**: Custom property name to avoid Panda3D conflicts
- **Encoding**: UTF-8 encoding for international character support

### Best Practices Established
1. Always use type hints for new methods
2. Keep private implementation details with __ prefix
3. Use settings manager for configurable values
4. Implement interfaces for new major components
5. Test changes after each refactoring step
6. Commit frequently with descriptive messages, one commit per working subject
7. Separate concerns into appropriate packages
8. Use camelCase for all new method names (except tests)
9. Format code with spaces: function( param ), array[ index ], variable = value
10. Use consistent bracket and operator spacing throughout codebase
11. **ALWAYS work on side branches, NEVER directly on master**
12. Create feature branches with descriptive names (feature/add-new-feature)
13. Test all changes before merging to master branch
14. Maintain clean git history with meaningful commit messages
15. **NEVER merge without explicit permission**
16. After merge: update master and create new branch immediately
17. Order imports from shortest to longest, group by type
18. Avoid getattr()/hasattr() - use direct access or try/except instead
19. **Avoid pyramid of doom** - max 2 nested if levels, use early returns
20. **Use custom exceptions** - create specific exception classes, avoid generic Exception catching
21. **Prefer early returns** - validate inputs early and return, avoid deep nesting
22. **Use guard clauses** - check preconditions at function start

## Future Development Guidelines
- **CRITICAL**: Always work on side branches, never directly on master
- **PERMISSION REQUIRED**: Never merge without explicit permission
- **POST-MERGE WORKFLOW**: Update master and create new branch after every merge
- Continue using established architecture patterns
- Add new settings to JSON configuration files
- Maintain type safety in all new code
- Use interface-based design for new components
- Keep test files in tests/ directory with snake_case naming
- Follow camelCase convention for all non-test code
- Apply consistent code formatting with bracket and operator spacing
- Use settings manager for code formatting preferences when generating code
- Create feature branches with descriptive names before starting work
- Test all changes thoroughly before merging
- Use workflow settings manager to check branch recommendations
- Commit each working subject separately with descriptive messages
- Order imports from shortest to longest with proper grouping
- Avoid getattr()/hasattr() patterns in favor of direct access or try/except
- **Avoid pyramid of doom**: Keep nesting to max 2 levels, use early returns
- **Use custom exceptions**: Create specific exception classes for different error types
- **Prefer flat code structure**: Use guard clauses and early returns over deep nesting
