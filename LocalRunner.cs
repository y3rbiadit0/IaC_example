using Amazon.Lambda.APIGatewayEvents;
using DotNetEnv;

namespace IaC_example
{
    class LocalRunner
    {
        static async Task Main()
        {
            
            if (EnvironmentSettings.Instance.IsDebugging)
            {
                await LocalLambdaProxy.RunDebuggingServer(async (request) =>
                {
                    var lambda = new LambdaApp();
                    return await lambda.HandlerAsync(request);
                },
                routePrefix: "fibonacci",
                port: 5000);
                return;
            }

        }

        private static APIGatewayProxyRequest MockRequest()
        {
            return new APIGatewayProxyRequest
            {
                QueryStringParameters = new Dictionary<string, string>
                {
                    { "number", "10" }
                }
            };
        }
    }
}
