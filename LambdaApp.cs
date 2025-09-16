using System;
using System.Threading.Tasks;
using Amazon.Lambda.Core;
using Amazon.Lambda.APIGatewayEvents;
using System.Text.Json;

[assembly: LambdaSerializer(typeof(Amazon.Lambda.Serialization.SystemTextJson.DefaultLambdaJsonSerializer))]

namespace IaC_example
{
    public class LambdaApp
    {
        public async Task<APIGatewayProxyResponse> HandlerAsync(APIGatewayProxyRequest request)
        {

            uint number = ParseInput(request);
            long fib = Fibonacci(number);
            string env = EnvironmentSettings.Instance.CurrentEnvironment.ToString();
            var secretNames = new List<string>
            {
                "net/MySQL/production",
                "net/MySQL/main",
                "prod/tpn",
                "net/M2M/production",
                "secret_example"
            };

            var secretsDict = new Dictionary<string, object>();
            foreach (var name in secretNames)
            {
                secretsDict[name] = await SecretsManagerUtil.GetSecretAsync(name);
            }


            var responseBody = new
            {
                result = fib,
                environment = env,
                secrets = secretsDict
            };


            return new APIGatewayProxyResponse
            {
                StatusCode = 200,
                Body = JsonSerializer.Serialize(responseBody),
                Headers = new Dictionary<string, string> { { "Content-Type", "application/json" } }
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

        private static long Fibonacci(uint value)
        {
            if (value == 0 || value == 1) return 1;
            return Fibonacci(value - 1) + Fibonacci(value - 2);
        }
    }
}
