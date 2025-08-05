using System.ComponentModel.DataAnnotations;

namespace HrRagApi.Models;

public class User
{
    public Guid UserId { get; set; } = Guid.NewGuid();
    //public virtual ICollection<Query> Queries { get; set; } = new List<Query>();
    public ICollection<Query> Queries { get; set; } = new List<Query>();
    

    [Required]
    [MaxLength(50)]
    public string Username { get; set; } = null!;

    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}