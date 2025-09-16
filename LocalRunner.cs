using Amazon.Lambda.APIGatewayEvents;
using DotNetEnv;

namespace IaC_example
{
    class LocalRunner
    {
        static async Task Main()
        {
            Env.Load();

            var app = new LambdaApp();
            APIGatewayProxyRequest mockRequest = MockRequest();

            var response = await app.HandlerAsync(mockRequest);

            Console.WriteLine("=== Local Lambda Debug ===");
            Console.WriteLine(response.Body);
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
