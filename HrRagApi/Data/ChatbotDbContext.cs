using Microsoft.EntityFrameworkCore;
using HrRagApi.Models;

namespace HrRagApi.Data
{
    public class ChatbotDbContext : DbContext
    {
        public ChatbotDbContext(DbContextOptions<ChatbotDbContext> options)
            : base(options) { }

        public DbSet<User> Users { get; set; } = null!;
        public DbSet<Query> Queries { get; set; } = null!;
        public DbSet<Response> Responses { get; set; } = null!;
        public DbSet<ResponseSource> ResponseSources { get; set; } = null!;

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            modelBuilder.Entity<Response>()
                .HasOne(r => r.Query)
                .WithOne(q => q.Response)
                .HasForeignKey<Response>(r => r.QueryId)
                .OnDelete(DeleteBehavior.Cascade);

            modelBuilder.Entity<Query>()
                .HasOne(q => q.User)
                .WithMany(u => u.Queries)
                .HasForeignKey(q => q.UserId)
                .OnDelete(DeleteBehavior.Cascade);

            modelBuilder.Entity<Response>()
                .HasMany(r => r.Sources)
                .WithOne(s => s.Response)
                .HasForeignKey(s => s.ResponseId)
                .OnDelete(DeleteBehavior.Cascade);

            modelBuilder.Entity<ResponseSource>()
                .Property(rs => rs.Content)
                .IsRequired();

            modelBuilder.Entity<ResponseSource>()
                .Property(rs => rs.Source)
                .IsRequired();
        }
    }
}