namespace ContosoLoanCleaner.Normalizers;

public interface IFieldNormalizer<T>
{
    T Normalize(T input);
    bool IsValid(T input);
}
