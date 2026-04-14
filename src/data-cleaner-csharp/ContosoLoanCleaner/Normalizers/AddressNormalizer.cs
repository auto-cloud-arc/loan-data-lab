namespace ContosoLoanCleaner.Normalizers;

public class AddressNormalizer : IFieldNormalizer<string>
{
    private static readonly HashSet<string> ValidStateCodes = new(StringComparer.OrdinalIgnoreCase)
    {
        "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA",
        "KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ",
        "NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT",
        "VA","WA","WV","WI","WY","DC"
    };

    public string Normalize(string input)
    {
        if (string.IsNullOrWhiteSpace(input))
            return string.Empty;

        return input.Trim().ToUpperInvariant();
    }

    public bool IsValid(string input)
    {
        return !string.IsNullOrWhiteSpace(input) && ValidStateCodes.Contains(input.Trim());
    }

    public static string NormalizeZipCode(string zipCode)
    {
        if (string.IsNullOrWhiteSpace(zipCode))
            return string.Empty;

        var digits = new string(zipCode.Where(char.IsDigit).ToArray());
        return digits.Length >= 5 ? digits[..5] : digits;
    }

    public static bool IsValidZipCode(string zipCode)
    {
        var normalized = NormalizeZipCode(zipCode);
        return normalized.Length == 5;
    }
}
