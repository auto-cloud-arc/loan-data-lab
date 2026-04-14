using ContosoLoanCleaner.Normalizers;
using Xunit;

namespace ContosoLoanCleaner.Tests.Normalizers;

public class PhoneNormalizerTests
{
    private readonly PhoneNormalizer _normalizer = new();

    [Theory]
    [InlineData("5555551234", "(555) 555-1234")]
    [InlineData("555-555-1234", "(555) 555-1234")]
    [InlineData("(555) 555-1234", "(555) 555-1234")]
    [InlineData("15555551234", "(555) 555-1234")]
    [InlineData("+1 (555) 555-1234", "(555) 555-1234")]
    public void Normalize_ValidPhone_ReturnsStandardFormat(string input, string expected)
    {
        Assert.Equal(expected, _normalizer.Normalize(input));
    }

    [Theory]
    [InlineData("5555551234", true)]
    [InlineData("555-555-1234", true)]
    [InlineData("123", false)]
    [InlineData("", false)]
    public void IsValid_ReturnsExpected(string input, bool expected)
    {
        Assert.Equal(expected, _normalizer.IsValid(input));
    }
}
