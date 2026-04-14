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
            HeaderValidated = null,
            MissingFieldFound = null,
            BadDataFound = context =>
                _logger.LogWarning("Malformed CSV token detected at row {Row}.",
                    context.Context?.Parser?.Row)
        };

        using var reader = new StreamReader(filePath);
        using var csv = new CsvReader(reader, config);

        var records = csv.GetRecords<LoanApplication>();
        foreach (var record in records)
        {
            _logger.LogDebug("Parsed application {AppId}.", record.ApplicationId);
            yield return record;
        }
    }
}
