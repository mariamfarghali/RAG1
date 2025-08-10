using System.ComponentModel.DataAnnotations;

namespace HrRagApi.Models;

public class User
{
    public Guid UserId { get; set; } = Guid.NewGuid(); //version 4 -> intialized randomly
    public ICollection<Query> Queries { get; set; } = new List<Query>();
    
    [Required]
    [MaxLength(50)]
    public string Username { get; set; } = null!;

    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}