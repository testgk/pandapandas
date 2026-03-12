"""
GUI Settings Manager - Loads and manages GUI configuration from JSON
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional


class GuiSettingsManager:
    """Manages GUI settings loaded from JSON configuration file"""

    def __init__(self, settingsFile: Optional[str] = None):
        if settingsFile is None:
            settingsFile = Path(__file__).parent / "gui_settings.json"

        self.__settingsFile = Path(settingsFile)
        self.__settings: Dict[str, Any] = {}
        self.__loadSettings()

    def __loadSettings(self) -> None:
        """Load settings from JSON file"""
        try:
            with open(self.__settingsFile, 'r', encoding='utf-8') as f:
                self.__settings = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load GUI settings from {self.__settingsFile}: {e}")
            self.__settings = {}

    def getButtonColor(self, buttonType: str, colorType: str) -> Tuple[float, float, float, float]:
        """Get button color as RGBA tuple"""
        try:
            color = self.__settings["colors"]["buttons"][buttonType][colorType]
            return tuple(color)
        except KeyError:
            # Fallback colors
            defaults = {
                "increment": {"background": (0.2, 0.8, 0.2, 1.0), "text": (0, 0, 0, 1.0)},
                "control": {"background": (0.1, 0.3, 0.1, 1.0), "text": (0, 1.0, 0, 1.0), "pressed": (0.5, 0.5, 0.5, 1.0)},
                "label": {"background": (0, 0, 0, 0), "text": (1.0, 1.0, 1.0, 1.0)},
                "game": {"background": (0.2, 0.2, 0.8, 1.0), "text": (1.0, 1.0, 1.0, 1.0), "pressed": (0.1, 0.1, 0.4, 1.0)}
            }
            return defaults.get(buttonType, {}).get(colorType, (1.0, 1.0, 1.0, 1.0))

    def getTextColor(self, textType: str) -> tuple[Any] | tuple[float, float, float, float]:
        """Get text color as RGBA tuple"""
        try:
            color = self.__settings["colors"]["text"][textType]
            return tuple(color)
        except KeyError:
            return 1.0, 1.0, 1.0, 1.0  # Default white

    def getButtonPosition(self, buttonGroup: str, positionKey: str) -> tuple[Any] | tuple[float, float, float]:
        """Get button position as XYZ tuple"""
        try:
            position = self.__settings["layout"]["buttons"][buttonGroup][positionKey]
            return tuple(position)
        except KeyError:
            return (0.0, 0.0, 0.0)  # Default center

    def getButtonScale(self, buttonGroup: str) -> float:
        """Get button scale factor"""
        try:
            return self.__settings["layout"]["buttons"][buttonGroup]["scale"]
        except KeyError:
            return 0.05  # Default scale

    def getTextPosition(self, positionKey: str) -> tuple[Any] | tuple[float, float]:
        """Get text position as XY tuple"""
        try:
            position = self.__settings["layout"]["text"][positionKey]
            return tuple(position)
        except KeyError:
            return 0.0, 0.0

    def getTextScale(self, scaleKey: str) -> float:
        """Get text scale factor"""
        try:
            return self.__settings["layout"]["text"][scaleKey]
        except KeyError:
            return 0.04

    def getChallengeTextSettings( self ) -> Dict[ str, Any ]:
        """Get challenge label position, scale and wordwrap"""
        text = self.__settings.get( "layout", {} ).get( "text", {} )
        return {
            "pos": tuple( text.get( "challenge_position", [ -1.3, -0.75 ] ) ),
            "scale": text.get( "challenge_scale", 0.036 ),
            "wordwrap": text.get( "challenge_wordwrap", 26 ),
            "max_lines": text.get( "challenge_max_lines", 14 ),
        }

    def getDebugTextSettings( self ) -> Dict[ str, Any ]:
        """Get debug label position, scale and wordwrap"""
        text = self.__settings.get( "layout", {} ).get( "text", {} )
        return {
            "pos": tuple( text.get( "debug_position", [ 0.5, -0.75 ] ) ),
            "scale": text.get( "debug_scale", 0.030 ),
            "wordwrap": text.get( "debug_wordwrap", 40 ),
        }

    def getPresetPositions(self) -> list[tuple[Any]] | list[tuple[float, int, float]]:
        """Get all preset button positions"""
        try:
            positions = self.__settings["layout"]["buttons"]["presets"]["positions"]
            return [tuple(pos) for pos in positions]
        except KeyError:
            return [(-0.6, 0, 0.2), (-0.6, 0, 0.1), (-0.6, 0, 0.0),
                   (0.6, 0, 0.2), (0.6, 0, 0.1), (0.6, 0, 0.0)]

    def getPresetLabels(self) -> List[str]:
        """Get preset button labels"""
        try:
            return self.__settings["text_content"]["presets"]
        except KeyError:
            return ["EUROPE", "AMERICAS", "ASIA", "AFRICA", "ATLANTIC", "PACIFIC"]

    def getTextContent(self, contentKey: str) -> str:
        """Get text content string"""
        try:
            return self.__settings["text_content"][contentKey]
        except KeyError:
            defaults = {
                "status_message": "REAL WORLD DATA • MANUAL CONTROLS ONLY",
                "system_ready": "SYSTEM READY",
                "zoom_label": "ZOOM"
            }
            return defaults.get(contentKey, "")

    def getEffectDuration(self) -> float:
        """Get button press effect duration"""
        try:
            return self.__settings["effects"]["button_press_duration"]
        except KeyError:
            return 0.1

    def getMaxLogMessages(self) -> int:
        """Get maximum number of log messages to display"""
        try:
            return self.__settings["effects"]["max_log_messages"]
        except KeyError:
            return 3

    def getLogWordWrap(self) -> int:
        """Get log text word wrap length"""
        try:
            return self.__settings["layout"]["text"]["log_wordwrap"]
        except KeyError:
            return 80

    def getCodeFormattingSpacing(self, spacingType: str) -> bool:
        """Get code formatting spacing preference"""
        try:
            return self.__settings["code_formatting"]["spacing"][spacingType]
        except KeyError:
            # Default spacing preferences
            defaults = {
                "after_opening_brackets": True,
                "before_closing_brackets": True,
                "before_equals": True,
                "after_equals": True
            }
            return defaults.get(spacingType, True)

    def shouldSpaceAfterOpeningBrackets(self) -> bool:
        """Check if spaces should be added after opening brackets ( [ {"""
        return self.getCodeFormattingSpacing("after_opening_brackets")

    def shouldSpaceBeforeClosingBrackets(self) -> bool:
        """Check if spaces should be added before closing brackets ) ] }"""
        return self.getCodeFormattingSpacing("before_closing_brackets")

    def shouldSpaceBeforeEquals(self) -> bool:
        """Check if spaces should be added before equals sign"""
        return self.getCodeFormattingSpacing("before_equals")

    def shouldSpaceAfterEquals(self) -> bool:
        """Check if spaces should be added after equals sign"""
        return self.getCodeFormattingSpacing("after_equals")

    def formatAssignment(self, variable: str, value: str) -> str:
        """Format assignment statement with proper spacing"""
        beforeSpace = " " if self.shouldSpaceBeforeEquals() else ""
        afterSpace = " " if self.shouldSpaceAfterEquals() else ""
        return f"{variable}{beforeSpace}={afterSpace}{value}"

    def formatFunctionCall(self, functionName: str, parameters: str) -> str:
        """Format function call with proper bracket spacing"""
        afterOpen = " " if self.shouldSpaceAfterOpeningBrackets() else ""
        beforeClose = " " if self.shouldSpaceBeforeClosingBrackets() else ""
        return f"{functionName}({afterOpen}{parameters}{beforeClose})"

    def formatArrayAccess(self, arrayName: str, index: str) -> str:
        """Format array access with proper bracket spacing"""
        afterOpen = " " if self.shouldSpaceAfterOpeningBrackets() else ""
        beforeClose = " " if self.shouldSpaceBeforeClosingBrackets() else ""
        return f"{arrayName}[{afterOpen}{index}{beforeClose}]"

    def formatDictLiteral(self, content: str) -> str:
        """Format dictionary literal with proper brace spacing"""
        afterOpen = " " if self.shouldSpaceAfterOpeningBrackets() else ""
        beforeClose = " " if self.shouldSpaceBeforeClosingBrackets() else ""
        return f"{{{afterOpen}{content}{beforeClose}}}"

    def shouldAlwaysUseSideBranch(self) -> bool:
        """Check if development should always happen on side branches"""
        try:
            return self.__settings["workflow_preferences"]["git"]["always_use_side_branch"]
        except KeyError:
            return True  # Default to safe practice

    def shouldNeverWorkDirectlyOnMaster(self) -> bool:
        """Check if direct work on master branch should be avoided"""
        try:
            return self.__settings["workflow_preferences"]["git"]["never_work_directly_on_master"]
        except KeyError:
            return True  # Default to safe practice

    def shouldAutoCreateFeatureBranch(self) -> bool:
        """Check if feature branches should be created automatically"""
        try:
            return self.__settings["workflow_preferences"]["git"]["auto_create_feature_branch"]
        except KeyError:
            return True

    def getBranchNamingPattern(self) -> str:
        """Get the preferred branch naming pattern"""
        try:
            return self.__settings["workflow_preferences"]["git"]["branch_naming_pattern"]
        except KeyError:
            return "feature/{description}"

    def shouldCommitFrequently(self) -> bool:
        """Check if frequent commits are preferred"""
        try:
            return self.__settings["workflow_preferences"]["development"]["commit_frequently"]
        except KeyError:
            return True

    def shouldUseDescriptiveCommitMessages(self) -> bool:
        """Check if descriptive commit messages are required"""
        try:
            return self.__settings["workflow_preferences"]["development"]["descriptive_commit_messages"]
        except KeyError:
            return True

    def shouldTestBeforeMerge(self) -> bool:
        """Check if testing before merge is required"""
        try:
            return self.__settings["workflow_preferences"]["development"]["test_before_merge"]
        except KeyError:
            return True

    def shouldMaintainCleanHistory(self) -> bool:
        """Check if clean git history should be maintained"""
        try:
            return self.__settings["workflow_preferences"]["development"]["maintain_clean_history"]
        except KeyError:
            return True

    def generateBranchName(self, branchType: str, description: str) -> str:
        """Generate a branch name following the established pattern"""
        pattern = self.getBranchNamingPattern()

        # Replace placeholder with actual description
        branchName = pattern.replace("{description}", description.lower().replace(" ", "-"))

        # Handle different branch types
        if branchType.lower() != "feature":
            branchName = branchName.replace("feature/", f"{branchType.lower()}/")

        return branchName

    def getWorkflowRecommendation(self, currentBranch: str) -> str:
        """Get workflow recommendation based on current branch"""
        if currentBranch == "master" and self.shouldNeverWorkDirectlyOnMaster():
            return "⚠️ WARNING: Working directly on master branch is not recommended. Create a feature branch instead."
        elif currentBranch.startswith(("feature/", "bugfix/", "refactor/", "experimental/")):
            return "✅ Good practice: Working on a dedicated branch."
        else:
            return "ℹ️ Consider using a descriptive branch name with prefix (feature/, bugfix/, etc.)"

    def shouldNeverMergeWithoutPermission(self) -> bool:
        """Check if merges require explicit permission"""
        try:
            return self.__settings["workflow_preferences"]["git"]["never_merge_without_permission"]
        except KeyError:
            return True  # Default to requiring permission

    def shouldUpdateMasterAfterMerge(self) -> bool:
        """Check if master should be updated after merge"""
        try:
            return self.__settings["workflow_preferences"]["git"]["update_master_after_merge"]
        except KeyError:
            return True

    def shouldCreateNewBranchAfterMerge(self) -> bool:
        """Check if new branch should be created after merge"""
        try:
            return self.__settings["workflow_preferences"]["git"]["create_new_branch_after_merge"]
        except KeyError:
            return True

    def shouldCommitEachWorkingSubject(self) -> bool:
        """Check if each working subject should get its own commit"""
        try:
            return self.__settings["workflow_preferences"]["git"]["commit_each_working_subject"]
        except KeyError:
            return True

    def shouldOrderImportsShortToLong(self) -> bool:
        """Check if imports should be ordered from short to long"""
        try:
            return self.__settings["workflow_preferences"]["development"]["order_imports_short_to_long"]
        except KeyError:
            return True

    def shouldAvoidGetAttrHasAttr(self) -> bool:
        """Check if getattr/hasattr should be avoided"""
        try:
            return self.__settings["workflow_preferences"]["development"]["avoid_getattr_hasattr"]
        except KeyError:
            return True

    def shouldAvoidPyramidOfDoom(self) -> bool:
        """Check if pyramid of doom (deep nesting) should be avoided"""
        try:
            return self.__settings["workflow_preferences"]["development"]["avoid_pyramid_of_doom"]
        except KeyError:
            return True

    def shouldUseTryExceptWithCustomExceptions(self) -> bool:
        """Check if try-except with custom exceptions is preferred"""
        try:
            return self.__settings["workflow_preferences"]["development"]["use_try_except_with_custom_exceptions"]
        except KeyError:
            return True

    def getMaxNestedIfLevels(self) -> int:
        """Get maximum allowed nested if levels"""
        try:
            return self.__settings["workflow_preferences"]["development"]["max_nested_if_levels"]
        except KeyError:
            return 2

    def shouldPreferEarlyReturn(self) -> bool:
        """Check if early return pattern is preferred"""
        try:
            return self.__settings["workflow_preferences"]["development"]["prefer_early_return"]
        except KeyError:
            return True

    def getMergeWorkflowSteps(self) -> List[str]:
        """Get the steps for proper merge workflow"""
        try:
            return self.__settings["workflow_preferences"]["merge_workflow"]["steps"]
        except KeyError:
            return [
                "1. Get permission before merging",
                "2. Test all changes thoroughly",
                "3. Merge feature branch to master",
                "4. Switch to master and pull latest",
                "5. Create new feature branch for next work"
            ]

    def generateMergeWorkflow(self, featureBranch: str, nextFeatureDescription: str) -> str:
        """Generate complete merge workflow instructions"""
        steps = self.getMergeWorkflowSteps()
        nextBranch = self.generateBranchName("feature", nextFeatureDescription)

        workflow = "📋 MERGE WORKFLOW:\n"
        workflow += "\n".join(steps)
        workflow += f"\n\n🔄 COMMANDS:\n"
        workflow += f"git checkout master\n"
        workflow += f"git pull origin master\n"
        workflow += f"git merge {featureBranch}\n"
        workflow += f"git push origin master\n"
        workflow += f"git checkout -b {nextBranch}\n"

        return workflow

    def orderImports(self, imports: List[str]) -> List[str]:
        """Order imports from shortest to longest"""
        if not self.shouldOrderImportsShortToLong():
            return imports

        # Separate standard library, third-party, and local imports
        standard_imports = []
        third_party_imports = []
        local_imports = []

        for imp in imports:
            if imp.startswith(('from os', 'from sys', 'from math', 'from json', 'from typing')):
                standard_imports.append(imp)
            elif imp.startswith(('from panda3d', 'from direct', 'from shapely', 'from geopandas')):
                third_party_imports.append(imp)
            else:
                local_imports.append(imp)

        # Sort each group by length
        standard_imports.sort(key=len)
        third_party_imports.sort(key=len)
        local_imports.sort(key=len)

        # Combine with blank lines between groups
        result = []
        if standard_imports:
            result.extend(standard_imports)
        if third_party_imports:
            if result:
                result.append("")  # Blank line separator
            result.extend(third_party_imports)
        if local_imports:
            if result:
                result.append("")  # Blank line separator
            result.extend(local_imports)

        return result

    def getCodeStyleViolations(self, code: str) -> List[str]:
        """Check for code style violations based on preferences"""
        violations = []

        if self.shouldAvoidGetAttrHasAttr():
            if 'getattr(' in code:
                violations.append("⚠️ Avoid using getattr() - use direct attribute access or properties instead")
            if 'hasattr(' in code:
                violations.append("⚠️ Avoid using hasattr() - use try/except or isinstance() instead")

        if self.shouldAvoidPyramidOfDoom():
            # Count nested if levels
            lines = code.split('\n')
            current_nesting = 0
            max_nesting = 0

            for line in lines:
                stripped = line.lstrip()
                indent_level = len(line) - len(stripped)

                if stripped.startswith('if '):
                    current_nesting = (indent_level // 4) + 1
                    max_nesting = max(max_nesting, current_nesting)

            if max_nesting > self.getMaxNestedIfLevels():
                violations.append(f"⚠️ Pyramid of doom detected: {max_nesting} nested if levels (max: {self.getMaxNestedIfLevels()}). Use early returns or guard clauses.")

        if self.shouldUseTryExceptWithCustomExceptions():
            # Check for generic exception handling
            if 'except:' in code or 'except Exception:' in code:
                violations.append("⚠️ Use specific custom exceptions instead of generic Exception catching")

            # Check for missing custom exceptions in try blocks
            if 'try:' in code and 'except ' in code:
                if not any(word in code for word in ['Error', 'Exception']) or 'Exception:' in code:
                    violations.append("ℹ️ Consider using custom exception classes for better error handling")

        return violations

    def generateBetterCodeExample(self, badCode: str) -> str:
        """Generate a better version of problematic code"""
        improvements = []

        # Example of fixing pyramid of doom
        if self.shouldAvoidPyramidOfDoom() and 'if ' in badCode and '    if ' in badCode:
            improvements.append("""
# BAD - Pyramid of doom:
if condition1:
    if condition2:
        if condition3:
            do_something()

# BETTER - Early returns:
if not condition1:
    return

if not condition2:
    return

if not condition3:
    return

do_something()
""")

        # Example of better exception handling
        if self.shouldUseTryExceptWithCustomExceptions() and 'except:' in badCode:
            improvements.append("""
# BAD - Generic exception:
try:
    risky_operation()
except:
    handle_error()

# BETTER - Custom exceptions:
class DataLoadError(Exception):
    pass

class ValidationError(Exception):
    pass

try:
    risky_operation()
except DataLoadError as e:
    handle_data_error(e)
except ValidationError as e:
    handle_validation_error(e)
""")

        return "\n".join(improvements) if improvements else "No improvements suggested."

    def getCodeQualityPatterns(self) -> Dict[str, str]:
        """Get code quality patterns and examples"""
        try:
            patterns = {}
            patterns.update(self.__settings["workflow_preferences"]["code_quality"]["exception_patterns"])
            patterns.update(self.__settings["workflow_preferences"]["code_quality"]["structure_patterns"])
            return patterns
        except KeyError:
            return {
                "custom_exceptions": "class CustomError(Exception): pass",
                "try_except_preferred": "try: action() except CustomError as e: handle(e)",
                "early_return": "if not condition: return early_result",
                "guard_clauses": "Validate inputs at function start with early returns"
            }

