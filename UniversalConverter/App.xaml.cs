using Microsoft.UI.Xaml;
using System.Linq;
using System.Threading.Tasks;
using Windows.ApplicationModel.Activation;

namespace UniversalConverter
{
    public partial class App : Application
    {
        public static Window m_window { get; private set; }

        public App()
        {
            this.InitializeComponent();
            var savedLang = Windows.Storage.ApplicationData.Current.LocalSettings.Values["language"] as string;
            if (!string.IsNullOrEmpty(savedLang))
            {
                Windows.Globalization.ApplicationLanguages.PrimaryLanguageOverride = savedLang;
            }
        }

        protected override async void OnLaunched(LaunchActivatedEventArgs args)
        {
            await ActivateAsync();
        }

        protected override async void OnActivated(IActivatedEventArgs args)
        {
            object activationArg = null;
            if (args is FileActivatedEventArgs fileArgs && fileArgs.Files.Any())
            {
                activationArg = fileArgs.Files[0];
            }
            await ActivateAsync(activationArg);
        }

        private async Task ActivateAsync(object activationArgs = null)
        {
            if (m_window == null)
            {
                await StatsService.LoadAsync();
                await PresetService.LoadPresetsAsync();

                m_window = new MainWindow();

                var savedTheme = Windows.Storage.ApplicationData.Current.LocalSettings.Values["theme"] as string;
                if (m_window.Content is FrameworkElement rootElement)
                {
                    switch (savedTheme)
                    {
                        case "Light": rootElement.RequestedTheme = ElementTheme.Light; break;
                        case "Dark": rootElement.RequestedTheme = ElementTheme.Dark; break;
                        default: rootElement.RequestedTheme = ElementTheme.Default; break;
                    }
                }
            }

            if (activationArgs != null && m_window.Content is MainWindow mainWindow)
            {
                mainWindow.NavigateToPageWithParameter(typeof(ConverterPage), activationArgs);
            }

            m_window.Activate();
        }
    }
}