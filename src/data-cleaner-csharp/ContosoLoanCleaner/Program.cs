using ContosoLoanCleaner.Models;
using ContosoLoanCleaner.Normalizers;
using ContosoLoanCleaner.Parsers;
using ContosoLoanCleaner.Security;
using ContosoLoanCleaner.Validators;
using CsvHelper;
using Microsoft.Extensions.Logging;
using Serilog;
using System.Text.Json;

Log.Logger = new LoggerConfiguration()
    .Enrich.FromLogContext()
    .WriteTo.Console(outputTemplate: "[{Timestamp:HH:mm:ss} {Level:u3}] {Message:lj}{NewLine}{Exception}")
    .CreateLogger();

try
{
    return await RunAsync(args);
}
catch (Exception ex)
{
    Log.Logger.Fatal(ex, "Unhandled application failure.");
    return ExitCodes.UnexpectedError;
}
finally
{
    Log.CloseAndFlush();
}

static async Task<int> RunAsync(string[] args)
{
    using var loggerFactory = LoggerFactory.Create(builder =>
        builder.AddSerilog(dispose: true));

    var logger = loggerFactory.CreateLogger<Program>();

    if (args.Length < 2)
    {
        logger.LogError("Usage: ContosoLoanCleaner <input-csv-path> <output-csv-path> [exception-report-path]");
        return ExitCodes.UsageError;
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

    try
    {
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
    }
    catch (FileNotFoundException ex)
    {
        logger.LogError(ex, "Input file could not be found at path {InputPath}.", inputPath);
        return ExitCodes.InputOutputError;
    }
    catch (DirectoryNotFoundException ex)
    {
        logger.LogError(ex, "Input directory could not be found for path {InputPath}.", inputPath);
        return ExitCodes.InputOutputError;
    }
    catch (CsvHelperException ex)
    {
        logger.LogError(ex, "CSV parsing failed for {InputPath}.", inputPath);
        return ExitCodes.ParseError;
    }
    catch (FormatException ex)
    {
        logger.LogError(ex, "Data formatting failed while processing {InputPath}.", inputPath);
        return ExitCodes.ParseError;
    }
    catch (UnauthorizedAccessException ex)
    {
        logger.LogError(ex, "Access denied while processing input or output files.");
        return ExitCodes.InputOutputError;
    }
    catch (IOException ex)
    {
        logger.LogError(ex, "I/O failure while processing input or output files.");
        return ExitCodes.InputOutputError;
    }

    try
    {
        EnsureParentDirectoryExists(outputPath);
        EnsureParentDirectoryExists(reportPath);

        // Write cleaned output CSV
        using (var writer = new StreamWriter(outputPath))
        {
            using var csv = new CsvHelper.CsvWriter(writer, System.Globalization.CultureInfo.InvariantCulture);
            csv.WriteRecords(cleanedRecords);
        }

        // Write exception report — PII fields are redacted for compliance.
        var safeExceptions = report.Exceptions.Select(e => new
        {
            e.ApplicationId,
            e.FieldName,
            e.RuleName,
            ActualValue = PiiRedactor.RedactFieldValue(e.FieldName, e.ActualValue),
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
    }
    catch (UnauthorizedAccessException ex)
    {
        logger.LogError(ex, "Access denied while writing output artifacts.");
        return ExitCodes.InputOutputError;
    }
    catch (IOException ex)
    {
        logger.LogError(ex, "I/O failure while writing output artifacts.");
        return ExitCodes.InputOutputError;
    }

    logger.LogInformation("Cleaning complete. {Cleaned}/{Total} records passed. Report: {Report}",
        report.CleanedRecords, report.TotalRecords, reportPath);

    return ExitCodes.Success;
}

static void EnsureParentDirectoryExists(string filePath)
{
    var directory = Path.GetDirectoryName(filePath);
    if (!string.IsNullOrWhiteSpace(directory) && !Directory.Exists(directory))
    {
        Directory.CreateDirectory(directory);
    }
}

internal static class ExitCodes
{
    public const int Success = 0;
    public const int UsageError = 1;
    public const int InputOutputError = 3;
    public const int ParseError = 4;
    public const int UnexpectedError = 5;
}
