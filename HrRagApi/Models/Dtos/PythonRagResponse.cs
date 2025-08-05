namespace HrRagApi.Models.Dtos
{
    public class PythonSourceDto
    {
        public string Content { get; set; } = string.Empty;
        public string Source { get; set; } = "Unknown";
        public int Page { get; set; }
    }

    public class PythonRagResponse
    {
        public string Question { get; set; } = string.Empty;
        public string Answer { get; set; } = string.Empty;
        public int ProcessingTimeMs { get; set; }
        public double Confidence { get; set; }
        public List<PythonSourceDto> Sources { get; set; } = new();
    }
}
