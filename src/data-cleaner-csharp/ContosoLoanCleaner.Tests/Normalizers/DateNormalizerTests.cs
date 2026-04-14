using ContosoLoanCleaner.Normalizers;
using Xunit;

namespace ContosoLoanCleaner.Tests.Normalizers;

public class DateNormalizerTests
{
    private readonly DateNormalizer _normalizer = new();

    [Theory]
    [InlineData("2024-01-15", "2024-01-15")]
    [InlineData("01/15/2024", "2024-01-15")]
    [InlineData("15-Jan-2024", "2024-01-15")]
    [InlineData("20240115", "2024-01-15")]
    [InlineData(" 2024-01-15 ", "2024-01-15")]
    public void Normalize_ValidDate_ReturnsIsoFormat(string input, string expected)
    {
        Assert.Equal(expected, _normalizer.Normalize(input));
    }

    [Fact]
    public void Normalize_InvalidDate_ReturnsTrimmedOriginalValue()
    {
        Assert.Equal("not-a-date", _normalizer.Normalize("  not-a-date  "));
    }

    [Theory]
    [InlineData("not-a-date", false)]
    [InlineData("", false)]
    [InlineData("2024-01-15", true)]
    public void IsValid_ReturnsExpected(string input, bool expected)
    {
        Assert.Equal(expected, _normalizer.IsValid(input));
    }

    [Fact]
    public void IsValidApplicationDate_FutureDate_ReturnsFalse()
    {
        var futureDate = DateTime.UtcNow.AddDays(1).ToString("yyyy-MM-dd");
        Assert.False(_normalizer.IsValidApplicationDate(futureDate));
    }

    [Fact]
    public void IsValidApplicationDate_TodayDate_ReturnsTrue()
    {
        var today = DateTime.UtcNow.ToString("yyyy-MM-dd");
        Assert.True(_normalizer.IsValidApplicationDate(today));
    }

    [Fact]
    public void IsValidApplicationDate_UsesReferenceDate()
    {
        Assert.True(_normalizer.IsValidApplicationDate("2024-01-15", new DateTime(2024, 1, 15)));
        Assert.False(_normalizer.IsValidApplicationDate("2024-01-16", new DateTime(2024, 1, 15)));
    }
}
