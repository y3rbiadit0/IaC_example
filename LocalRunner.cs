namespace IaC_example
{
    class LocalRunner
    {
        static async Task Main()
        {

            if (EnvironmentSettings.Instance.IsDebugging)
            {
                await LocalLambdaProxy.RunLocalProxy(async (request) =>
                {
                    var lambda = new LambdaApp();
                    return await lambda.HandlerAsync(request);
                },
                routePrefix: "fibonacci",
                port: 5000);
                return;
            }

        }

    }
}
