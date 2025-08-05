namespace HrRagApi.Models
{
    public class ResponseSource
    {
        public int ResponseSourceId { get; set; }
        public int ResponseId { get; set; }
        public string Content { get; set; } = string.Empty;
        public string Source { get; set; } = string.Empty;
        public int Page { get; set; }
        public Response Response { get; set; } = null!;
    }

}
