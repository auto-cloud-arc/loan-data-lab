# 1. Product Requirements Document (PRD): .NET Calculator with xUnit Testing

1.1 Document Information

**Version:** 1.0

**Author:** GitHub Copilot

**Date:** November 3rd, 2025

**Status:** Draft

1.2 Executive Summary

This document describes the requirements for developing a basic .NET 8.0 console calculator application with comprehensive xUnit testing. The calculator will support standard arithmetic operations and be designed with a focus on testability, maintainability, and proper error handling.

1.3 Problem Statement

Developers need a practical example of a well-structured .NET application that demonstrates:

Basic calculator functionality with support for essential arithmetic operations

Proper application structure with testable components

Implementation of unit testing with xUnit framework

Effective error handling and input validation

The solution will serve as both a functional calculator and a reference implementation for .NET best practices.

1.4 Goals and Objectives

Create a fully functional calculator application using .NET 8.0 and C#
Implement core arithmetic operations (+, -, \*, /) using case expressions

Demonstrate proper C# coding practices including null handling, error management, and code organization

Refactor code from using case expressions to methods for better testability
Demonstrate incremental development by adding modulo and exponent operations
Provide comprehensive xUnit tests with different test approaches (fact, theory)
Enable a clean, interactive console experience with proper user feedback
Showcase proper solution structure with separate application and test projects

1.5 Scope

1.5.1 In Scope

PowerShell script to set up the solution and project structure
.NET 8.0 console application using top-level statements
Calculator core arithmetic operations (addition, subtraction, multiplication, division, modulo, exponent)
User input handling with proper validation
xUnit test project with comprehensive test coverage
Method refactoring for testability
Proper error handling and null safety
Documentation for both application code and tests

1.5.2 Out of Scope

GUI implementation
Advanced mathematical functions (logarithms, trigonometry, etc.)
Persistence of calculations
Scientific calculator features
Multi-language support
Calculator history feature

1.6.1 Epic Requirements

As a developer, I want to create a .NET 8 console calculator application that performs basic arithmetic operations so that I can demonstrate best practices in .NET development.

1.6.2 User Stories / Use Cases

As a user, I want to perform basic arithmetic calculations with two operands so that I can quickly compute results
As a user, I want clear prompts and feedback during calculation so I can understand how to use the application
As a user, I want to perform multiple calculations in sequence so I don't have to restart the application
As a user, I want proper error handling so invalid inputs don't crash the application
As a developer, I want well-structured and tested code so that I can understand best practices in .NET development

As a developer, I want to refactor the .NET 8 console calculator application by adding an Angular UI frontend while maintaining existing console project and testing functionality.

As a QA tester, I want comprehensive unit tests with xUnit and Playwright with Jest so I can verify the calculator functions correctly

As an Azure Architect, I want add a custom work item type architectural_decision_record to deploy the calculator application to Azure App Service so that it is accessible via a web interface.

1.7 Functional Requirements

| Requirement ID | Description |

| -------------- | --------------------------------------------------------------------------------------- |

| FR-1 | The application shall prompt users for two numeric operands and one operator |

| FR-2 | The application shall support addition (+) operations between two numbers |

| FR-3 | The application shall support subtraction (-) operations between two numbers |

| FR-4 | The application shall support multiplication (\*) operations between two numbers |

| FR-5 | The application shall support division (/) operations between two numbers |

| FR-6 | The application shall support modulo (%) operations between two numbers |

| FR-7 | The application shall support exponent (^) operations between two numbers |

| FR-8 | The application shall display the result of each calculation to the user |

| FR-9 | The application shall handle division by zero errors gracefully |

| FR-10 | The application shall validate user input and provide feedback for invalid entries |

| FR-11 | The application shall allow users to perform additional calculations without restarting |

| FR-12 | The application shall confirm with the user before exiting |

| FR-13 | The application shall clear the screen between calculations for a clean interface |

| FR-14 | Each arithmetic operation shall be implemented as a separate, testable method |

| FR-15 | The application shall properly handle null inputs to prevent runtime exceptions |

1.8 Non-Functional Requirements

**Performance:** The calculator shall provide immediate feedback for all operations
**Usability:** The console interface shall be intuitive with clear instructions for users
**Reliability:** The application shall handle edge cases and invalid inputs without crashing
**Testability:** All core functionality shall be covered by unit tests
**Maintainability:** Code shall follow C# best practices and be well-documented

**Compatibility:** The application shall run on any platform supporting .NET 8.0

1.9 Assumptions and Dependencies

Development will use .NET 8.0 SDK
xUnit will be used as the testing framework
Developers have access to appropriate .NET development tools
The application will use standard C# console I/O features

No external libraries beyond .NET Standard and xUnit are required

1.9.1 Compatible Package Versions for .NET 8.0

To ensure compatibility with .NET 8.0, the following package versions **MUST** be used. Using newer versions will cause test discovery failures and build errors:

| Package | Version | Reason |
| --- | --- | --- |
| xunit | 2.6.2 | Supports .NET 8.0; newer versions (2.9.3+) cause test discovery failures with net8.0 |
| xunit.runner.visualstudio | 2.5.1 | Compatible with .NET 8.0; newer versions (3.1.4+) lack netcoreapp3.1 support |
| Microsoft.NET.Test.Sdk | 17.5.0 | Supports .NET 8.0; newer versions (17.14.1+) cause compatibility issues |
| coverlet.collector | 6.0.0 | Latest stable version supporting .NET 8.0 |

**Critical Notes:**

- The test project must include `<SuppressTfmSupportBuildErrors>true</SuppressTfmSupportBuildErrors>` in the PropertyGroup to suppress build warnings about .NET 8.0 being out of support
- Using newer package versions (e.g., xunit 2.9.3, xunit.runner.visualstudio 3.1.4, Microsoft.NET.Test.Sdk 17.14.1) will result in test discovery finding only 1 test instead of 49, and build failures
- If package versions are incorrect, manually update the .csproj file ItemGroup to match the versions above

1.10 Success Criteria / KPIs

All specified calculator operations work correctly
Unit tests cover all arithmetic operations with multiple test cases
The console application runs without crashing when given valid or invalid input
All build and test commands execute successfully
Code meets appropriate null safety standards for C#
Documentation is clear and comprehensive

1.11 Milestones & Timeline

Solution Setup
Create PowerShell script for initializing solution structure
Set up the .NET 8.0 console application and xUnit test project

Initial Implementation
Implement basic calculator operations with top-level statements
Build and test the initial version

Refactoring
Convert operations to testable methods
Add proper error handling and screen clearing
Make methods public for testing accessibility

Testing
Create comprehensive xUnit tests for all operations
Implement both fact and theory test approaches
Ensure all tests pass

Final Improvements
Add modulo and exponent operations
Document the code
Fix any remaining issues or warnings

Documentation
Update documentation
Create setup and cleanup scripts

1.12 Implementation Guidance

1.12.1 Solution Setup

Create a PowerShell script named `Set-DotnetSlnForCalculator.ps1` in "$(git rev-parse --show-toplevel)\src\workspace" that:
Creates a solution folder named `calculator-xunit-testing`
Sets up a new solution using `dotnet new sln`
Adds a console application project named `calculator` using `dotnet new console`
Adds an xUnit test project named `calculator.tests` using `dotnet new xunit`
Configures appropriate project references between projects
Changes default file names from `Program.cs` to `Calculator.cs` and from `UnitTest1.cs` to `CalculatorTest.cs`
Manually updates both project files to target .NET 8.0 (TargetFramework=net8.0)
Sets SuppressTfmSupportBuildErrors=true in test project PropertyGroup to support xUnit on .NET 8.0
Updates package versions to match section 1.9.1 compatible versions (xunit 2.6.2, xunit.runner.visualstudio 2.5.1, Microsoft.NET.Test.Sdk 17.5.0)
Builds the solution to verify successful setup
Execute the powershell script to create the solution structure

**Implementation Notes:**

- The `dotnet new` command does not support `--force-framework` option; use standard templates and update TargetFramework in .csproj files post-creation
- Target framework **MUST** be manually set to `net8.0` in both calculator.csproj and calculator.tests.csproj PropertyGroup sections (NOT net10.0 or other versions)
- **CRITICAL**: The setup script must explicitly update the TargetFramework property in the console app project (calculator.csproj) immediately after creation, as `dotnet new console` creates projects targeting the latest framework version by default
- Package versions **MUST** match the compatible versions in section 1.9.1; newer versions are incompatible with .NET 8.0 and will cause build failures
- The SuppressTfmSupportBuildErrors configuration is required because xUnit test SDK versions are newer than .NET 8.0 support lifecycle

1.12.2 Calculator Implementation

**File Structure:** Proper separation of concerns is critical for avoiding C# compilation errors:

- **Calculator.cs**: Contains the Calculator class definition with all arithmetic methods (public static Add, Subtract, Multiply, Divide, Modulo, Power, Calculate)
- **Program.cs**: Contains top-level statements for console interaction (prompts, loops, user feedback)

**CRITICAL:** Top-level statements and class/namespace declarations cannot coexist in the same file. Violating this causes error CS8803: "Top-level statements must precede namespace and type declarations."

Implement the calculator logic:
Define the Calculator class with methods for each operation in Calculator.cs
Implement top-level statements for user prompts and console interaction in Program.cs
Prompt for first operand, second operand, and operator
Perform the appropriate arithmetic operation
Display the result
Ask if the user wants to perform another calculation
Handle user response to continue or exit
Fix null reference warnings using appropriate null handling techniques

1.12.3 Refactoring Steps

Convert each arithmetic operation into its own method for testability
Make methods public to allow testing from the xUnit project
Add screen clearing for a better user experience
Implement modulo and exponent operations
Add proper null handling to prevent exceptions

1.12.4 Testing Strategy

Create xUnit tests for each calculator operation
Use Fact tests for simple assertions
Use Theory tests with InlineData for testing multiple cases
Include test cases for edge conditions (like division by zero)
Implement tests for normal, edge, and error cases
All tests must pass before completion

1.13 Cleanup Solution

Create a PowerShell script named `Remove-DotnetSlnForCalculator.ps1` in "$(git rev-parse --show-toplevel)\programming\dotnet\csharp\workspace" that:
Gets the repository root path using `git rev-parse --show-toplevel`
Constructs the path to the workspace folder: `{RepoRoot}\programming\dotnet\csharp\workspace`
Identifies the solution directory: `{Workspace}\calculator-xunit-testing`
Removes the entire `calculator-xunit-testing` folder and all its contents (calculator project, calculator.tests project, and solution file) recursively using `Remove-Item -Recurse -Force`
Provides user-friendly status messages indicating successful removal or any errors
Suggests the user re-run the setup script to recreate the solution if needed

**Execution:**
After creating the script, execute it from the workspace directory to remove the calculator solution:

```powershell
cd {RepoRoot}\programming\dotnet\csharp\workspace
.\Remove-DotnetSlnForCalculator.ps1
```

The script will completely remove the `calculator-xunit-testing` folder, allowing the workspace to be reset to its initial state.

1.14 Additional Learning Outcomes

Understanding .NET solution and project structure
Working with C# top-level statements
Understanding C# file structure constraints (top-level statements must precede class declarations)
Implementing proper null handling in C# code
Writing effective xUnit tests with different techniques
Creating reusable setup and cleanup scripts
Translating C# concepts to other languages (Python)
Managing package version compatibility across different .NET framework versions

1.15 Troubleshooting Guide

**Problem: Build error CS8803 - "Top-level statements must precede namespace and type declarations"**

- Cause: Top-level statements and class declarations are in the same file
- Solution: Ensure Calculator class is in Calculator.cs and top-level statements are in Program.cs

**Problem: Only 1 test discovered instead of 49**

- Cause: Incorrect package versions (likely xunit 2.9.3+ or xunit.runner.visualstudio 3.1.4+)
- Solution: Update .csproj file to use versions from section 1.9.1 (xunit 2.6.2, xunit.runner.visualstudio 2.5.1, Microsoft.NET.Test.Sdk 17.5.0)

**Problem: Target framework mismatch or "Assets file doesn't have a target for 'net8.0'"**

- Cause: Project files targeting wrong framework (e.g., net10.0 instead of net8.0)
- Solution: Verify both calculator.csproj and calculator.tests.csproj have `<TargetFramework>net8.0</TargetFramework>`

**Problem: Test file corrupted or reverted**

- Cause: Previous failed operations may have reverted CalculatorTest.cs to stub implementation
- Solution: Re-run section 1.12.4 testing strategy to restore full 49-test implementation

**Problem: Build succeeds but tests don't run**

- Cause: Stale build artifacts from framework version changes
- Solution: Execute `dotnet clean` followed by `dotnet restore` and `dotnet build` before running tests

**Problem: Setup script creates projects targeting net10.0 instead of net8.0**

- Cause: The `dotnet new` command creates projects using the latest framework version by default; the setup script must explicitly update the TargetFramework property in .csproj files
- Solution: The setup script must programmatically replace `<TargetFramework>` in both calculator.csproj and calculator.tests.csproj after project creation to ensure they target net8.0. Use regex replacement: `-replace '<TargetFramework>.*?</TargetFramework>', '<TargetFramework>net8.0</TargetFramework>'`
