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
    print(f"Never merge without permission: {settings.shouldNeverMergeWithoutPermission()}")
    print(f"Update master after merge: {settings.shouldUpdateMasterAfterMerge()}")
    print(f"Create new branch after merge: {settings.shouldCreateNewBranchAfterMerge()}")
    print(f"Branch naming pattern: {settings.getBranchNamingPattern()}")

    print("\nDevelopment Preferences:")
    print(f"Commit frequently: {settings.shouldCommitFrequently()}")
    print(f"Commit each working subject: {settings.shouldCommitEachWorkingSubject()}")
    print(f"Descriptive commit messages: {settings.shouldUseDescriptiveCommitMessages()}")
    print(f"Test before merge: {settings.shouldTestBeforeMerge()}")
    print(f"Maintain clean history: {settings.shouldMaintainCleanHistory()}")
    print(f"Order imports short to long: {settings.shouldOrderImportsShortToLong()}")
    print(f"Avoid getattr/hasattr: {settings.shouldAvoidGetAttrHasAttr()}")

    print("\nBranch Name Generation:")
    print(f"Feature branch: {settings.generateBranchName('feature', 'add new component')}")
    print(f"Bugfix branch: {settings.generateBranchName('bugfix', 'fix camera issue')}")
    print(f"Refactor branch: {settings.generateBranchName('refactor', 'improve performance')}")

    print("\nWorkflow Recommendations:")
    print(f"On master: {settings.getWorkflowRecommendation('master')}")
    print(f"On feature branch: {settings.getWorkflowRecommendation('feature/new-component')}")
    print(f"On other branch: {settings.getWorkflowRecommendation('my-branch')}")

    print("\nMerge Workflow:")
    steps = settings.getMergeWorkflowSteps()
    for step in steps:
        print(f"  {step}")


def testCodeStyleChecks():
    """Test code style checking functionality"""
    settings = GuiSettingsManager()

    print("\nCode Style Tests:")

    # Test import ordering
    test_imports = [
        "from panda3d.core import *",
        "from os import path",
        "from typing import Dict, List",
        "from settings.gui_settings_manager import GuiSettingsManager",
        "from direct.showbase.ShowBase import ShowBase"
    ]

    print("Original imports:")
    for imp in test_imports:
        print(f"  {imp}")

    ordered_imports = settings.orderImports(test_imports)
    print("\nOrdered imports:")
    for imp in ordered_imports:
        if imp == "":
            print()  # Blank line
        else:
            print(f"  {imp}")

    # Test code style violations
    bad_code = """
    if hasattr(obj, 'method'):
        value = getattr(obj, 'attribute', default)
    """

    violations = settings.getCodeStyleViolations(bad_code)
    print("\nCode style violations found:")
    for violation in violations:
        print(f"  {violation}")

    # Test merge workflow generation
    print("\nGenerated Merge Workflow:")
    workflow = settings.generateMergeWorkflow("feature/current-work", "add new feature")
    print(workflow)


def runAllTests():
    """Run all configuration tests"""
    testCodeFormattingSettings()
    testWorkflowSettings()
    testCodeStyleChecks()


if __name__ == "__main__":
    runAllTests()
