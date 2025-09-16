using Amazon.Lambda.APIGatewayEvents;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;

namespace IaC_example
{
    /// <summary>
    /// Runs a local HTTP server to proxy API Gateway requests to Lambda handlers for local testing.
    /// </summary>
    public static class LocalLambdaProxy
    {
        /// <summary>
        /// Starts a local HTTP server that routes POST requests to a Lambda handler.
        /// </summary>
        /// <param name="lambdaHandler">The Lambda handler to invoke.</param>
        /// <param name="routePrefix">The route prefix for this Lambda (e.g., "query").</param>
        /// <param name="port">The port to run the local server on.</param>
        private static void Run(
            Func<APIGatewayProxyRequest, Task<APIGatewayProxyResponse>> lambdaHandler,
            string routePrefix = "query",
            int port = 5000)
        {
            var builder = WebApplication.CreateBuilder();
            var app = builder.Build();
            app.MapGet($"/{routePrefix}", async (HttpRequest request) =>
            {
                // Read query parameter "number"
                request.Query.TryGetValue("number", out var numberValues);
                string numberStr = numberValues.Count > 0 ? numberValues[0] : "1";

                // Build APIGatewayProxyRequest
                var apiEvent = new APIGatewayProxyRequest
                {
                    Path = request.Path,
                    HttpMethod = "POST",
                    QueryStringParameters = new Dictionary<string, string>
                    {
                        ["number"] = numberStr
                    }
                };

                // Invoke Lambda handler
                var response = await lambdaHandler(apiEvent);

                return Results.Content(response.Body ?? string.Empty, "application/json");
            });

            Console.WriteLine($"🚀 Local Lambda proxy running on http://0.0.0.0:{port}/{routePrefix}");
            app.Run($"http://0.0.0.0:{port}");
        }

        public static async Task RunDebuggingServer(
            Func<APIGatewayProxyRequest, Task<APIGatewayProxyResponse>> handler,
            string routePrefix = "query",
            int port = 5000)
        {
            Console.WriteLine("Waiting for debugger to attach...");
            while (!System.Diagnostics.Debugger.IsAttached)
            {
                await Task.Delay(500);
            }

            Console.WriteLine("Debugger attached.");
            Console.WriteLine("Starting local proxy server for Postman...");

            Run(handler, routePrefix, port);
        }
    }
}
