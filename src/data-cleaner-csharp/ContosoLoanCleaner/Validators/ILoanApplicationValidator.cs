using ContosoLoanCleaner.Models;

namespace ContosoLoanCleaner.Validators;

public interface ILoanApplicationValidator
{
    IEnumerable<ValidationResult> Validate(LoanApplication application);
}
