using System.Text.RegularExpressions;

namespace ContosoLoanCleaner.Normalizers;

public class PhoneNormalizer : IFieldNormalizer<string>
{
    private static readonly Regex DigitsOnly = new(@"\D", RegexOptions.Compiled);

    public string Normalize(string input)
    {
        if (string.IsNullOrWhiteSpace(input))
            return string.Empty;

        var digits = DigitsOnly.Replace(input.Trim(), string.Empty);

        if (digits.Length == 11 && digits.StartsWith('1'))
            digits = digits[1..];

        if (digits.Length == 10)
            return $"({digits[..3]}) {digits[3..6]}-{digits[6..]}";

        return input.Trim();
    }

    public bool IsValid(string input)
    {
        if (string.IsNullOrWhiteSpace(input))
            return false;

        var digits = DigitsOnly.Replace(input.Trim(), string.Empty);
        if (digits.Length == 11 && digits.StartsWith('1'))
            digits = digits[1..];

        return digits.Length == 10;
    }
}
