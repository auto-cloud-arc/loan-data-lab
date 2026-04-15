namespace ContosoLoanCleaner.Models;

public class LoanApplication
{
    public string ApplicationId { get; set; } = string.Empty;
    public string CustomerId { get; set; } = string.Empty;
    public string BranchCode { get; set; } = string.Empty;
    public decimal LoanAmount { get; set; }
    public string LoanType { get; set; } = string.Empty;
    public string ApplicationDate { get; set; } = string.Empty;
    public string FirstName { get; set; } = string.Empty;
    public string LastName { get; set; } = string.Empty;
    public string Ssn { get; set; } = string.Empty;
    public string PhoneNumber { get; set; } = string.Empty;
    public string AddressLine1 { get; set; } = string.Empty;
    public string City { get; set; } = string.Empty;
    public string StateCode { get; set; } = string.Empty;
    public string ZipCode { get; set; } = string.Empty;
    public string Email { get; set; } = string.Empty;
    public decimal? CollateralValue { get; set; }
}
