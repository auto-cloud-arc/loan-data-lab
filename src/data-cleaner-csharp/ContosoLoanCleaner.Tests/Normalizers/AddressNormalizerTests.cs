using ContosoLoanCleaner.Normalizers;
using Xunit;

namespace ContosoLoanCleaner.Tests.Normalizers;

public class AddressNormalizerTests
{
    private readonly AddressNormalizer _normalizer = new();

    [Theory]
    [InlineData("ca", "CA")]
    [InlineData("ny", "NY")]
    [InlineData("  TX  ", "TX")]
    public void Normalize_StateCode_ReturnsUpperTrimmed(string input, string expected)
    {
        Assert.Equal(expected, _normalizer.Normalize(input));
    }

    [Theory]
    [InlineData("CA", true)]
    [InlineData("ca", true)]
    [InlineData("XX", false)]
    [InlineData("", false)]
    [InlineData("  ", false)]
    public void IsValid_StateCode_ReturnsExpected(string input, bool expected)
    {
        Assert.Equal(expected, _normalizer.IsValid(input));
    }

    [Theory]
    [InlineData("90210", "90210")]
    [InlineData("90210-1234", "90210")]
    [InlineData("  10001  ", "10001")]
    public void NormalizeZipCode_ReturnsFirst5Digits(string input, string expected)
    {
        Assert.Equal(expected, AddressNormalizer.NormalizeZipCode(input));
    }

    [Theory]
    [InlineData("90210", true)]
    [InlineData("9021", false)]
    [InlineData("", false)]
    public void IsValidZipCode_ReturnsExpected(string input, bool expected)
    {
        Assert.Equal(expected, AddressNormalizer.IsValidZipCode(input));
    }
}
