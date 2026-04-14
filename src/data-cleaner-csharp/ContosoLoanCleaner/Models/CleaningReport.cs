namespace ContosoLoanCleaner.Models;

public class CleaningReport
{
    public DateTime GeneratedAt { get; set; } = DateTime.UtcNow;
    public string InputFile { get; set; } = string.Empty;
    public string OutputFile { get; set; } = string.Empty;
    public int TotalRecords { get; set; }
    public int CleanedRecords { get; set; }
    public int ExceptionRecords { get; set; }
    public List<ValidationResult> Exceptions { get; set; } = new();

    public double SuccessRate => TotalRecords == 0 ? 0 : (double)CleanedRecords / TotalRecords * 100;
}
