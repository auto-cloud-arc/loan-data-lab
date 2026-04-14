using ContosoLoanCleaner.Models;

namespace ContosoLoanCleaner.Parsers;

public interface ILoanApplicationParser
{
    IEnumerable<LoanApplication> Parse(string filePath);
}
