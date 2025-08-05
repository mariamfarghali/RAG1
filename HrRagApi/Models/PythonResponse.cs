namespace HrRagApi.Models;

public class PythonResponse
{
    public string Answer { get; set; } = null!;
    public int ProcessingTimeMs { get; set; }
    public double Confidence { get; set; }

}