namespace IaC_example
{
    public enum AppEnvironment
    {
        Unknown,
        Local,
        Stage,
        Production
    }

    public sealed class EnvironmentSettings
    {
        private EnvironmentSettings() { }

        private static readonly Lazy<EnvironmentSettings> _instance = new(() => new EnvironmentSettings());
        public static EnvironmentSettings Instance => _instance.Value;

        public AppEnvironment CurrentEnvironment =>
            (Environment.GetEnvironmentVariable("IAC_ENVIRONMENT") ?? string.Empty)
            .ToLowerInvariant() switch
            {
                "local" => AppEnvironment.Local,
                "stage" => AppEnvironment.Stage,
                "production" => AppEnvironment.Production,
                _ => AppEnvironment.Unknown
            };

        public bool IsDebugging => CurrentEnvironment == AppEnvironment.Local;
        public bool IsDevelopment => CurrentEnvironment == AppEnvironment.Local || CurrentEnvironment == AppEnvironment.Stage;
        
        public bool IsProduction => CurrentEnvironment == AppEnvironment.Production;
    }
}
