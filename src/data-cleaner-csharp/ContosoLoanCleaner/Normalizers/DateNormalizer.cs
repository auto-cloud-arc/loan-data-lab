using System.Globalization;

namespace ContosoLoanCleaner.Normalizers;

public class DateNormalizer : IFieldNormalizer<string>
{
    private static readonly string[] SupportedFormats =
    [
        "yyyy-MM-dd", "MM/dd/yyyy", "M/d/yyyy", "MM-dd-yyyy",
        "dd-MMM-yyyy", "yyyy/MM/dd", "yyyyMMdd"
    ];

    public string Normalize(string input)
    {
        if (string.IsNullOrWhiteSpace(input))
            return string.Empty;

        if (TryParse(input, out var date))
            return date.ToString("yyyy-MM-dd", CultureInfo.InvariantCulture);

        return input.Trim();
    }

    public bool IsValid(string input)
    {
        return !string.IsNullOrWhiteSpace(input) && TryParse(input, out _);
    }

    public bool IsValidApplicationDate(string input, DateTime? referenceDate = null)
    {
        if (!TryParse(input, out var date))
            return false;

        var reference = referenceDate ?? DateTime.UtcNow;
        return date.Date <= reference.Date;
    }

    private static bool TryParse(string input, out DateTime result)
    {
        return DateTime.TryParseExact(input.Trim(), SupportedFormats,
            CultureInfo.InvariantCulture, DateTimeStyles.None, out result)
            || DateTime.TryParse(input.Trim(), CultureInfo.InvariantCulture,
            DateTimeStyles.None, out result);
    }
}
