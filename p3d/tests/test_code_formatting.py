"""
Test code formatting settings functionality
"""
from p3d.settings.gui_settings_manager import GuiSettingsManager


def testCodeFormattingSettings():
    """Test that code formatting settings work correctly"""
    settings = GuiSettingsManager()

    # Test spacing preferences
    print("Code Formatting Settings Test:")
    print(f"Space after opening brackets: {settings.shouldSpaceAfterOpeningBrackets()}")
    print(f"Space before closing brackets: {settings.shouldSpaceBeforeClosingBrackets()}")
    print(f"Space before equals: {settings.shouldSpaceBeforeEquals()}")
    print(f"Space after equals: {settings.shouldSpaceAfterEquals()}")

    # Test formatting methods
    print("\nFormatting Examples:")
    print(f"Assignment: {settings.formatAssignment('myVariable', 'someValue')}")
    print(f"Function call: {settings.formatFunctionCall('myFunction', 'param1, param2')}")
    print(f"Array access: {settings.formatArrayAccess('myArray', 'index')}")
    print(f"Dict literal: {settings.formatDictLiteral('key: value, key2: value2')}")


def testWorkflowSettings():
    """Test workflow and branch management settings"""
    settings = GuiSettingsManager()

    print("\nWorkflow Settings Test:")
    print(f"Always use side branch: {settings.shouldAlwaysUseSideBranch()}")
    print(f"Never work on master: {settings.shouldNeverWorkDirectlyOnMaster()}")
    print(f"Auto-create feature branch: {settings.shouldAutoCreateFeatureBranch()}")
    print(f"Branch naming pattern: {settings.getBranchNamingPattern()}")

    print("\nDevelopment Preferences:")
    print(f"Commit frequently: {settings.shouldCommitFrequently()}")
    print(f"Descriptive commit messages: {settings.shouldUseDescriptiveCommitMessages()}")
    print(f"Test before merge: {settings.shouldTestBeforeMerge()}")
    print(f"Maintain clean history: {settings.shouldMaintainCleanHistory()}")

    print("\nBranch Name Generation:")
    print(f"Feature branch: {settings.generateBranchName('feature', 'add new component')}")
    print(f"Bugfix branch: {settings.generateBranchName('bugfix', 'fix camera issue')}")
    print(f"Refactor branch: {settings.generateBranchName('refactor', 'improve performance')}")

    print("\nWorkflow Recommendations:")
    print(f"On master: {settings.getWorkflowRecommendation('master')}")
    print(f"On feature branch: {settings.getWorkflowRecommendation('feature/new-component')}")
    print(f"On other branch: {settings.getWorkflowRecommendation('my-branch')}")


def runAllTests():
    """Run all configuration tests"""
    testCodeFormattingSettings()
    testWorkflowSettings()


if __name__ == "__main__":
    runAllTests()
