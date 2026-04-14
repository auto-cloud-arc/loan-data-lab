using ContosoLoanCleaner.Models;
using ContosoLoanCleaner.Normalizers;
using ContosoLoanCleaner.Validators;
using Xunit;

namespace ContosoLoanCleaner.Tests.Validators;

public class LoanApplicationValidatorTests
{
    private readonly LoanApplicationValidator _validator = new(
        new AddressNormalizer(),
        new PhoneNormalizer(),
        new DateNormalizer());

    private static LoanApplication ValidApplication() => new()
    {
        ApplicationId = "APP-001",
        CustomerId = "CUST-001",
        BranchCode = "BR-01",
        LoanAmount = 250000,
        LoanType = "MORTGAGE",
        ApplicationDate = DateTime.UtcNow.AddDays(-1),
        PhoneNumber = "(555) 555-1234",
        StateCode = "CA",
        ZipCode = "90210",
        CollateralValue = 300000
    };

    [Fact]
    public void Validate_ValidApplication_ReturnsNoFailures()
    {
        var app = ValidApplication();
        var results = _validator.Validate(app).ToList();
        Assert.Empty(results);
    }

    [Fact]
    public void Validate_MissingApplicationId_ReturnsFailure()
    {
        var app = ValidApplication();
        app.ApplicationId = string.Empty;
        var results = _validator.Validate(app).ToList();
        Assert.Contains(results, r => r.RuleName == "RequiredField" && r.FieldName == "ApplicationId");
    }

    [Fact]
    public void Validate_NegativeLoanAmount_ReturnsFailure()
    {
        var app = ValidApplication();
        app.LoanAmount = -1000;
        var results = _validator.Validate(app).ToList();
        Assert.Contains(results, r => r.RuleName == "PositiveLoanAmount");
    }

    [Fact]
    public void Validate_FutureApplicationDate_ReturnsFailure()
    {
        var app = ValidApplication();
        app.ApplicationDate = DateTime.UtcNow.AddDays(5);
        var results = _validator.Validate(app).ToList();
        Assert.Contains(results, r => r.RuleName == "ApplicationDateNotFuture");
    }

    [Fact]
    public void Validate_MortgageWithoutCollateral_ReturnsFailure()
    {
        var app = ValidApplication();
        app.LoanType = "MORTGAGE";
        app.CollateralValue = null;
        var results = _validator.Validate(app).ToList();
        Assert.Contains(results, r => r.RuleName == "CollateralRequiredForSecuredLoan");
    }

    [Fact]
    public void Validate_InvalidStateCode_ReturnsFailure()
    {
        var app = ValidApplication();
        app.StateCode = "XX";
        var results = _validator.Validate(app).ToList();
        Assert.Contains(results, r => r.RuleName == "ValidStateCode");
    }

    [Fact]
    public void Validate_PersonalLoanWithoutCollateral_ReturnsNoCollateralFailure()
    {
        var app = ValidApplication();
        app.LoanType = "PERSONAL";
        app.CollateralValue = null;
        var results = _validator.Validate(app).ToList();
        Assert.DoesNotContain(results, r => r.RuleName == "CollateralRequiredForSecuredLoan");
    }
}
