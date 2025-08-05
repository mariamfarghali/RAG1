using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using HrRagApi.Data;
using HrRagApi.Models;
using HrRagApi.Models.Dtos;




[ApiController]
[Route("api/rag")]
public class RagController : ControllerBase
{
    private readonly ChatbotDbContext _db;
    private readonly IHttpClientFactory _httpClientFactory;
    private readonly ILogger<RagController> _logger;
    private readonly string _pythonBackendUrl;

    public RagController(
        ChatbotDbContext db,
        IHttpClientFactory httpClientFactory,
        IConfiguration configuration,
        ILogger<RagController> logger)
    {
        _db = db;
        _httpClientFactory = httpClientFactory;
        _logger = logger;
        _pythonBackendUrl = configuration["PythonBackend"]
            ?? throw new InvalidOperationException("PythonBackend URL is not configured");
    }

    [HttpPost("ask")]
    public async Task<IActionResult> AskQuestion([FromBody] HrRagApi.Models.QuestionRequest request)

    {
        if (request == null || string.IsNullOrWhiteSpace(request.Question) || string.IsNullOrWhiteSpace(request.Username))
        {
            return BadRequest("Invalid request");
        }

        using var transaction = await _db.Database.BeginTransactionAsync();

        try
        {
            // 1. Check if user exists by username or create new
            var user = await _db.Users.FirstOrDefaultAsync(u => u.Username == request.Username);
            if (user == null)
            {
                user = new User
                {
                    Username = request.Username
                    // UserId and CreatedAt are auto-handled
                };

                await _db.Users.AddAsync(user);
                await _db.SaveChangesAsync();
            }

            // 2. Save initial query
            var query = new Query
            {
                UserId = user.UserId,
                Question = request.Question,
                IpAddress = HttpContext.Connection.RemoteIpAddress?.ToString()
                            ?? IPAddress.Loopback.ToString(),
                Timestamp = DateTime.UtcNow
            };

            await _db.Queries.AddAsync(query);
            await _db.SaveChangesAsync();

            _logger.LogInformation("Saved query with ID {QueryId}", query.QueryId);

            // 3. Call Python RAG API
            var httpClient = _httpClientFactory.CreateClient("RagClient");

            var ragRequest = new { question = request.Question };

            var response = await httpClient.PostAsJsonAsync(_pythonBackendUrl, ragRequest);

            if (!response.IsSuccessStatusCode)
            {
                _logger.LogError("Python RAG API returned {StatusCode}", response.StatusCode);
                await transaction.RollbackAsync();
                return StatusCode(503, "RAG service unavailable");
            }

            var result = await response.Content.ReadFromJsonAsync<PythonRagResponse>();

            _logger.LogInformation("Response from Python: {@result}", result);
            if (result == null)
            {
                _logger.LogError("Received null response from Python RAG API");
                await transaction.RollbackAsync();
                return StatusCode(503, "Invalid response from RAG service");
            }

            // 4. Save response
            var dbResponse = new Response
            {
                QueryId = query.QueryId,
                Answer = result.Answer ?? string.Empty,
                ProcessingTimeMs = result.ProcessingTimeMs,
                ConfidenceScore = result.Confidence,
                Timestamp = DateTime.UtcNow,
                Query = query,
                Sources = new List<ResponseSource>()
            };

            await _db.Responses.AddAsync(dbResponse);
            await _db.SaveChangesAsync();

            if (result.Sources?.Count > 0)
            {
                var sources = result.Sources.Select(s => new ResponseSource
                {
                    ResponseId = dbResponse.ResponseId,
                    Content = s.Content ?? string.Empty,
                    Source = s.Source ?? "Unknown",
                    Page = s.Page,
                }).ToList();

                await _db.ResponseSources.AddRangeAsync(sources);
                await _db.SaveChangesAsync();

                dbResponse.Sources = sources;
                await _db.SaveChangesAsync();
            }

            await transaction.CommitAsync();

            return Ok(new RagResponseDto
            {
                Question = result.Question ?? request.Question,
                Answer = result.Answer ?? string.Empty,
                ProcessingTimeMs = result.ProcessingTimeMs,
                Confidence = result.Confidence,
                Sources = result.Sources?.Select(s => new SourceDto
                {
                    Content = s.Content ?? string.Empty,
                    Source = s.Source ?? "Unknown",
                    Page = s.Page
                }).ToList() ?? new List<SourceDto>(),
                QueryId = query.QueryId,
                ResponseId = dbResponse.ResponseId,
                Timestamp = DateTime.UtcNow
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error processing question");
            await transaction.RollbackAsync();
            return StatusCode(500, "Internal server error");
        }
    }


    [HttpGet("history/{userId}")]
    public async Task<IActionResult> GetUserHistory(Guid userId, [FromQuery] int limit = 20)
    {
        try
        {
            // Ensure userId comparison is between Guids
            var history = await _db.Queries
                .Where(q => q.UserId == userId)  // Both are Guid
                .Include(q => q.Response)
                    .ThenInclude(r => r.Sources)
                .OrderByDescending(q => q.Timestamp)
                .Take(limit)
                .Select(q => new QueryHistoryDto
                {
                    QueryId = q.QueryId,
                    Question = q.Question ?? string.Empty,
                    Answer = q.Response.Answer ?? string.Empty,
                    ProcessingTimeMs = q.Response.ProcessingTimeMs,
                    Confidence = q.Response.ConfidenceScore ?? 0,
                    Sources = q.Response.Sources.Select(s => new SourceDto
                    {
                        Content = s.Content ?? string.Empty,
                        Source = s.Source ?? "Unknown",
                        Page = s.Page
                    }).ToList(),
                    Timestamp = q.Timestamp
                })
                .ToListAsync();

            return Ok(history);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error retrieving history for user {UserId}", userId);
            return StatusCode(500, "Error retrieving history");
        }
    }
}

// DTO Classes

public class RagResponseDto
{
    public string Question { get; set; } = string.Empty;
    public string Answer { get; set; } = string.Empty;
    public int ProcessingTimeMs { get; set; }
    public double Confidence { get; set; }
    public List<SourceDto> Sources { get; set; } = new List<SourceDto>();
    public int QueryId { get; set; }
    public int ResponseId { get; set; }
    public DateTime Timestamp { get; set; }
}

public class QueryHistoryDto
{
    public int QueryId { get; set; }
    public string Question { get; set; } = string.Empty;
    public string Answer { get; set; } = string.Empty;
    public int ProcessingTimeMs { get; set; }
    public double Confidence { get; set; }
    public List<SourceDto> Sources { get; set; } = new List<SourceDto>();
    public DateTime Timestamp { get; set; }
}

public class SourceDto
{
    public string Content { get; set; } = string.Empty;
    public string Source { get; set; } = string.Empty;
    public int Page { get; set; }
}
public class QuestionRequest
{
    public Guid UserId { get; set; }
    public required string Question { get; set; }
    public string? Username { get; internal set; }
}