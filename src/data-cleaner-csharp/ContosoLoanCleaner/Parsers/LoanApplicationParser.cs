using System.Globalization;
using ContosoLoanCleaner.Models;
using CsvHelper;
using CsvHelper.Configuration;
using Microsoft.Extensions.Logging;

namespace ContosoLoanCleaner.Parsers;

public class LoanApplicationParser : ILoanApplicationParser
{
    private readonly ILogger<LoanApplicationParser> _logger;

    public LoanApplicationParser(ILogger<LoanApplicationParser> logger)
    {
        _logger = logger;
    }

    public IEnumerable<LoanApplication> Parse(string filePath)
    {
        if (!File.Exists(filePath))
            throw new FileNotFoundException($"Input file not found: {filePath}");

        var config = new CsvConfiguration(CultureInfo.InvariantCulture)
        {
            HasHeaderRecord = true,
            MissingFieldFound = null,
            BadDataFound = context =>
                _logger.LogWarning("Bad CSV data at row {Row}: {Field}",
                    context.Context?.Parser?.Row, context.Field)
        };

        using var reader = new StreamReader(filePath);
        using var csv = new CsvReader(reader, config);

        var records = csv.GetRecords<LoanApplication>();
        foreach (var record in records)
        {
            _logger.LogDebug("Parsed application {AppId} for customer {CustomerId}",
                record.ApplicationId, record.CustomerId);
            yield return record;
        }
    }
}
