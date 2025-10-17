using Microsoft.Extensions.DependencyInjection;
using System;

namespace UniversalConverter
{
    public static class AppServices
    {
        public static IServiceProvider Services { get; private set; }

        public static void ConfigureServices()
        {
            var services = new ServiceCollection();

            // Services
            services.AddSingleton<IWindowService, WindowService>();
            services.AddSingleton<ImageConverter>();

            // ViewModels
            services.AddTransient<ConverterViewModel>();
            services.AddTransient<QueueViewModel>();
            services.AddTransient<SettingsViewModel>();
            services.AddTransient<DashboardViewModel>();

            Services = services.BuildServiceProvider();
        }
    }
}