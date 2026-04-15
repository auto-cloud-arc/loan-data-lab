using ContosoLoanCleaner.Models;
using ContosoLoanCleaner.Normalizers;

namespace ContosoLoanCleaner.Validators;

public class LoanApplicationValidator : ILoanApplicationValidator
{
    private readonly AddressNormalizer _addressNormalizer;
    private readonly PhoneNormalizer _phoneNormalizer;
    private readonly DateNormalizer _dateNormalizer;

    private static readonly HashSet<string> ValidLoanTypes = new(StringComparer.OrdinalIgnoreCase)
    {
        "MORTGAGE", "AUTO", "PERSONAL", "HELOC", "BUSINESS"
    };

    public LoanApplicationValidator(
        AddressNormalizer addressNormalizer,
        PhoneNormalizer phoneNormalizer,
        DateNormalizer dateNormalizer)
    {
        _addressNormalizer = addressNormalizer;
        _phoneNormalizer = phoneNormalizer;
        _dateNormalizer = dateNormalizer;
    }

    public IEnumerable<ValidationResult> Validate(LoanApplication application)
    {
        var results = new List<ValidationResult>();

        if (string.IsNullOrWhiteSpace(application.ApplicationId))
            results.Add(Fail(application.ApplicationId, nameof(application.ApplicationId),
                "RequiredField", null, "Application ID is required."));

        if (string.IsNullOrWhiteSpace(application.CustomerId))
            results.Add(Fail(application.ApplicationId, nameof(application.CustomerId),
                "RequiredField", null, "Customer ID is required."));

        if (application.LoanAmount <= 0)
            results.Add(Fail(application.ApplicationId, nameof(application.LoanAmount),
                "PositiveLoanAmount", application.LoanAmount.ToString(),
                "Loan amount must be greater than zero."));

        if (!ValidLoanTypes.Contains(application.LoanType))
            results.Add(Fail(application.ApplicationId, nameof(application.LoanType),
                "ValidLoanType", application.LoanType,
                $"Loan type '{application.LoanType}' is not a recognized value."));

        if (!string.IsNullOrWhiteSpace(application.PhoneNumber) &&
            !_phoneNormalizer.IsValid(application.PhoneNumber))
            results.Add(Fail(application.ApplicationId, nameof(application.PhoneNumber),
                "ValidPhone", "***-***-****", "Phone number format is invalid."));

        if (!string.IsNullOrWhiteSpace(application.StateCode) &&
            !_addressNormalizer.IsValid(application.StateCode))
            results.Add(Fail(application.ApplicationId, nameof(application.StateCode),
                "ValidStateCode", application.StateCode, "State code is not a valid US state."));

        if (!string.IsNullOrWhiteSpace(application.ZipCode) &&
            !AddressNormalizer.IsValidZipCode(application.ZipCode))
            results.Add(Fail(application.ApplicationId, nameof(application.ZipCode),
                "ValidZipCode", application.ZipCode, "ZIP code must be 5 digits."));

        if (!string.IsNullOrWhiteSpace(application.ApplicationDate))
        {
            if (!_dateNormalizer.IsValid(application.ApplicationDate))
            {
                results.Add(Fail(application.ApplicationId, nameof(application.ApplicationDate),
                    "ValidApplicationDate", application.ApplicationDate,
                    "Application date must be a valid date."));
            }
            else if (!_dateNormalizer.IsValidApplicationDate(application.ApplicationDate))
            {
                results.Add(Fail(application.ApplicationId, nameof(application.ApplicationDate),
                    "ApplicationDateNotFuture", application.ApplicationDate,
                    "Application date cannot be in the future."));
            }
        }

        if (application.LoanType.Equals("MORTGAGE", StringComparison.OrdinalIgnoreCase) ||
            application.LoanType.Equals("HELOC", StringComparison.OrdinalIgnoreCase) ||
            application.LoanType.Equals("AUTO", StringComparison.OrdinalIgnoreCase))
        {
            if (!application.CollateralValue.HasValue || application.CollateralValue <= 0)
                results.Add(Fail(application.ApplicationId, nameof(application.CollateralValue),
                    "CollateralRequiredForSecuredLoan", application.CollateralValue?.ToString(),
                    $"Collateral value is required and must be positive for loan type '{application.LoanType}'."));
        }

        return results;
    }

    private static ValidationResult Fail(string appId, string field, string rule,
        string? actual, string message, ValidationSeverity severity = ValidationSeverity.Error)
        => new()
        {
            ApplicationId = appId,
            FieldName = field,
            RuleName = rule,
            ActualValue = actual,
            Message = message,
            Severity = severity
        };
}
