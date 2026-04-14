namespace ContosoLoanCleaner.Security;

public static class PiiRedactor
{
    private static readonly HashSet<string> SensitiveFields =
    [
        "Ssn",
        "FirstName",
        "LastName",
        "Email",
        "PhoneNumber",
        "AddressLine1"
    ];

    public static string? RedactFieldValue(string fieldName, string? value)
    {
        return SensitiveFields.Contains(fieldName, StringComparer.OrdinalIgnoreCase)
            ? "***REDACTED***"
            : value;
    }
}