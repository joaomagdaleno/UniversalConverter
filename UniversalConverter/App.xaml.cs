using Microsoft.UI.Xaml;

namespace UniversalConverter
{
    public partial class App : Application
    {
        public static Window m_window { get; private set; }

        public App()
        {
            this.InitializeComponent();

            // Load and apply language setting
            var savedLang = Windows.Storage.ApplicationData.Current.LocalSettings.Values["language"] as string;
            if (!string.IsNullOrEmpty(savedLang))
            {
                Windows.Globalization.ApplicationLanguages.PrimaryLanguageOverride = savedLang;
            }
        }

        protected override void OnLaunched(Microsoft.UI.Xaml.LaunchActivatedEventArgs args)
        {
            m_window = new MainWindow();

            // Load and apply theme setting
            var savedTheme = Windows.Storage.ApplicationData.Current.LocalSettings.Values["theme"] as string;
            if (m_window.Content is FrameworkElement rootElement)
            {
                switch (savedTheme)
                {
                    case "Light":
                        rootElement.RequestedTheme = ElementTheme.Light;
                        break;
                    case "Dark":
                        rootElement.RequestedTheme = ElementTheme.Dark;
                        break;
                    default:
                        rootElement.RequestedTheme = ElementTheme.Default;
                        break;
                }
            }

            m_window.Activate();
        }
    }
}