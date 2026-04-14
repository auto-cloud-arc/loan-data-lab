using ContosoLoanCleaner.Security;
using Xunit;

namespace ContosoLoanCleaner.Tests.Security;

public class PiiRedactorTests
{
    [Theory]
    [InlineData("Ssn")]
    [InlineData("Email")]
    [InlineData("FirstName")]
    [InlineData("LastName")]
    [InlineData("PhoneNumber")]
    [InlineData("AddressLine1")]
    public void RedactFieldValue_SensitiveField_ReturnsRedacted(string fieldName)
    {
        var result = PiiRedactor.RedactFieldValue(fieldName, "sensitive-value");

        Assert.Equal("***REDACTED***", result);
    }

    [Fact]
    public void RedactFieldValue_NonSensitiveField_ReturnsOriginalValue()
    {
        var result = PiiRedactor.RedactFieldValue("LoanType", "MORTGAGE");

        Assert.Equal("MORTGAGE", result);
    }
}