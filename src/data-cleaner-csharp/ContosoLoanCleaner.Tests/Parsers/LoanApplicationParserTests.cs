using ContosoLoanCleaner.Parsers;
using CsvHelper.TypeConversion;
using Microsoft.Extensions.Logging.Abstractions;
using Xunit;

namespace ContosoLoanCleaner.Tests.Parsers;

public class LoanApplicationParserTests
{
    private readonly LoanApplicationParser _parser = new(NullLogger<LoanApplicationParser>.Instance);

    [Fact]
    public void Parse_NonExistentFile_ThrowsFileNotFoundException()
    {
        Assert.Throws<FileNotFoundException>(() => _parser.Parse("/nonexistent/path/file.csv").ToList());
    }

    [Fact]
    public void Parse_ValidCsvFile_ReturnsRecords()
    {
        var csvPath = Path.Combine(Path.GetTempPath(), $"test_{Guid.NewGuid()}.csv");
        try
        {
            File.WriteAllText(csvPath,
                "ApplicationId,CustomerId,BranchCode,LoanAmount,LoanType,ApplicationDate,FirstName,LastName,Ssn,PhoneNumber,AddressLine1,City,StateCode,ZipCode,Email,CollateralValue\n" +
                "APP-001,CUST-001,BR-01,250000,MORTGAGE,2024-01-15,John,Doe,123-45-6789,5555551234,123 Main St,Los Angeles,CA,90210,jdoe@example.com,300000\n");

            var records = _parser.Parse(csvPath).ToList();
            Assert.Single(records);
            Assert.Equal("APP-001", records[0].ApplicationId);
            Assert.Equal(250000m, records[0].LoanAmount);
        }
        finally
        {
            if (File.Exists(csvPath))
                File.Delete(csvPath);
        }
    }

    [Fact]
    public void Parse_InvalidLoanAmount_ThrowsTypeConverterException()
    {
        var csvPath = Path.Combine(Path.GetTempPath(), $"test_{Guid.NewGuid()}.csv");
        try
        {
            File.WriteAllText(csvPath,
                "ApplicationId,CustomerId,BranchCode,LoanAmount,LoanType,ApplicationDate,FirstName,LastName,Ssn,PhoneNumber,AddressLine1,City,StateCode,ZipCode,Email,CollateralValue\n" +
                "APP-001,CUST-001,BR-01,INVALID_AMOUNT,MORTGAGE,2024-01-15,John,Doe,123-45-6789,5555551234,123 Main St,Los Angeles,CA,90210,jdoe@example.com,300000\n");

            Assert.Throws<TypeConverterException>(() => _parser.Parse(csvPath).ToList());
        }
        finally
        {
            if (File.Exists(csvPath))
                File.Delete(csvPath);
        }
    }

    [Fact]
    public void Parse_MissingHeaders_UsesDefaultsForUnmappedFields()
    {
        var csvPath = Path.Combine(Path.GetTempPath(), $"test_{Guid.NewGuid()}.csv");
        try
        {
            File.WriteAllText(csvPath,
                "ApplicationId,CustomerId\n" +
                "APP-001,CUST-001\n");

            var records = _parser.Parse(csvPath).ToList();

            Assert.Single(records);
            Assert.Equal("APP-001", records[0].ApplicationId);
            Assert.Equal("CUST-001", records[0].CustomerId);
            Assert.Equal(string.Empty, records[0].LoanType);
        }
        finally
        {
            if (File.Exists(csvPath))
                File.Delete(csvPath);
        }
    }
}
