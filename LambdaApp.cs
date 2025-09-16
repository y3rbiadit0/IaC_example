using System;
using System.Threading.Tasks;
using Amazon.Lambda.Core;
using Amazon.Lambda.APIGatewayEvents;

[assembly: LambdaSerializer(typeof(Amazon.Lambda.Serialization.SystemTextJson.DefaultLambdaJsonSerializer))]

namespace IaC_example
{
    public class LambdaApp
    {
        public async Task<APIGatewayProxyResponse> HandlerAsync(APIGatewayProxyRequest request)
        {
            string secretName = "secret_example";
            string secret = await SecretsManagerUtil.GetSecretAsync(secretName);

            uint number = ParseInput(request);

            long fib = Fibonacci(number);
            string body = PrepareBody(secret, number, fib);

            return new APIGatewayProxyResponse
            {
                StatusCode = 200,
                Body = body
            };
        }

        private static uint ParseInput(APIGatewayProxyRequest request)
        {
            uint number = 10;
            if (request.QueryStringParameters != null &&
                request.QueryStringParameters.TryGetValue("number", out string? value))
            {
                _ = uint.TryParse(value, out number);
            }

            return number;
        }

        private static string PrepareBody(string secret, uint number, long fib)
        {
            string env = EnvironmentSettings.Instance.CurrentEnvironment.ToString();

            string body = $"Environment: {env}\nFibonacci({number}) = {fib}\nSecret: {secret}\n";

            if (EnvironmentSettings.Instance.IsDevelopment)
                body += "Running in development mode: extra logs enabled.\n";

            if (EnvironmentSettings.Instance.IsProduction)
                body += "Running in production mode: optimized settings.\n";
            return body;
        }

        private static long Fibonacci(uint value)
        {
            if (value == 0 || value == 1) return 1;
            return Fibonacci(value - 1) + Fibonacci(value - 2);
        }
    }
}
