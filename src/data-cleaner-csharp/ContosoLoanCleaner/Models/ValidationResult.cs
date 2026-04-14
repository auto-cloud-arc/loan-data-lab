namespace ContosoLoanCleaner.Models;

public class ValidationResult
{
    public string ApplicationId { get; set; } = string.Empty;
    public string FieldName { get; set; } = string.Empty;
    public string RuleName { get; set; } = string.Empty;
    public string? ActualValue { get; set; }
    public string Message { get; set; } = string.Empty;
    public ValidationSeverity Severity { get; set; } = ValidationSeverity.Error;
}

public enum ValidationSeverity
{
    Info,
    Warning,
    Error,
    Critical
}
