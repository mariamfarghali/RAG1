namespace HrRagApi.Models;

public class Query
{
    public int QueryId { get; set; }  // Changed from Guid to int
    public Guid UserId { get; set; }   // Ensure this matches everywhere
    public User User { get; set; } = null!;
    public string Question { get; set; } = string.Empty;
    public string IpAddress { get; set; } = string.Empty;
    public DateTime Timestamp { get; set; }
    public Response Response { get; set; } = null!;
}