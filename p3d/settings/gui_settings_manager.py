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
                "control": {"background": (0.1, 0.3, 0.1, 1.0), "text": (0, 1.0, 0, 1.0)},
                "label": {"background": (0, 0, 0, 0), "text": (1.0, 1.0, 1.0, 1.0)}
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

