namespace HrRagApi.Models
{
    public class Response
    {
        public int ResponseId { get; set; }  // Changed from Guid to int
        public int QueryId { get; set; }     // Foreign key
        public string Answer { get; set; } = string.Empty;
        public int ProcessingTimeMs { get; set; }
        public double? ConfidenceScore { get; set; }
        public DateTime Timestamp { get; set; }
        public required Query Query { get; set; }
        public required List<ResponseSource> Sources { get; set; }
    }
}