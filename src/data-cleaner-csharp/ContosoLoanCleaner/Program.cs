using ContosoLoanCleaner.Models;
using ContosoLoanCleaner.Normalizers;
using ContosoLoanCleaner.Parsers;
using ContosoLoanCleaner.Validators;
using Microsoft.Extensions.Logging;
using Serilog;
using System.Text.Json;

Log.Logger = new LoggerConfiguration()
    .WriteTo.Console(outputTemplate: "[{Timestamp:HH:mm:ss} {Level:u3}] {Message:lj}{NewLine}{Exception}")
    .CreateLogger();

using var loggerFactory = LoggerFactory.Create(builder =>
    builder.AddSerilog(dispose: true));

var logger = loggerFactory.CreateLogger<Program>();

if (args.Length < 2)
{
    logger.LogError("Usage: ContosoLoanCleaner <input-csv-path> <output-csv-path> [exception-report-path]");
    return 1;
}

var inputPath = args[0];
var outputPath = args[1];
var reportPath = args.Length >= 3 ? args[2] : Path.ChangeExtension(outputPath, ".exceptions.json");

logger.LogInformation("Contoso Bank Loan Data Cleaner starting.");
logger.LogInformation("Input:  {InputPath}", inputPath);
logger.LogInformation("Output: {OutputPath}", outputPath);

var addressNormalizer = new AddressNormalizer();
var phoneNormalizer = new PhoneNormalizer();
var dateNormalizer = new DateNormalizer();
var validator = new LoanApplicationValidator(addressNormalizer, phoneNormalizer, dateNormalizer);
var parser = new LoanApplicationParser(loggerFactory.CreateLogger<LoanApplicationParser>());

var report = new CleaningReport
{
    InputFile = inputPath,
    OutputFile = outputPath,
    GeneratedAt = DateTime.UtcNow
};

var cleanedRecords = new List<LoanApplication>();

foreach (var app in parser.Parse(inputPath))
{
    report.TotalRecords++;

    // Normalize fields before validation
    app.StateCode = addressNormalizer.Normalize(app.StateCode);
    app.ZipCode = AddressNormalizer.NormalizeZipCode(app.ZipCode);
    app.PhoneNumber = phoneNormalizer.Normalize(app.PhoneNumber);
    app.LoanType = app.LoanType?.Trim().ToUpperInvariant() ?? string.Empty;

    var failures = validator.Validate(app).ToList();

    if (failures.Count == 0)
    {
        cleanedRecords.Add(app);
        report.CleanedRecords++;
    }
    else
    {
        report.Exceptions.AddRange(failures);
        report.ExceptionRecords++;
        logger.LogWarning("Application {AppId} has {Count} validation failure(s).",
            app.ApplicationId, failures.Count);
    }
}

// Write cleaned output CSV
using (var writer = new StreamWriter(outputPath))
{
    using var csv = new CsvHelper.CsvWriter(writer, System.Globalization.CultureInfo.InvariantCulture);
    csv.WriteRecords(cleanedRecords);
}

// Write exception report — PII fields (SSN, name, email) are redacted for compliance
var safeExceptions = report.Exceptions.Select(e => new
{
    e.ApplicationId,
    e.FieldName,
    e.RuleName,
    ActualValue = RedactPii(e.FieldName, e.ActualValue),
    e.Message,
    Severity = e.Severity.ToString()
});

var jsonOptions = new JsonSerializerOptions { WriteIndented = true };
await File.WriteAllTextAsync(reportPath,
    JsonSerializer.Serialize(new
    {
        report.GeneratedAt,
        report.TotalRecords,
        report.CleanedRecords,
        report.ExceptionRecords,
        SuccessRate = $"{report.SuccessRate:F1}%",
        Exceptions = safeExceptions
    },
    jsonOptions));

logger.LogInformation("Cleaning complete. {Cleaned}/{Total} records passed. Report: {Report}",
    report.CleanedRecords, report.TotalRecords, reportPath);

return 0;

static string? RedactPii(string fieldName, string? value)
{
    var piiFields = new HashSet<string>(StringComparer.OrdinalIgnoreCase)
        { "Ssn", "FirstName", "LastName", "Email" };
    return piiFields.Contains(fieldName) ? "***REDACTED***" : value;
}
