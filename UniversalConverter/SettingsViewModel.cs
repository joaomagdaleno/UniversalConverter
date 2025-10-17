using Microsoft.Extensions.DependencyInjection;
using System;
using System.ComponentModel;
using System.Runtime.CompilerServices;
using System.Threading.Tasks;
using System.Windows.Input;
using Windows.ApplicationModel;
using Windows.Management.Deployment;
using Windows.Storage;
using Microsoft.UI.Xaml;

namespace UniversalConverter
{
    public class SettingsViewModel : INotifyPropertyChanged
    {
        public IWindowService WindowService { get; set; }
        public ICommand CheckForUpdatesCommand { get; }
        public string AppVersion { get; private set; }
        private bool _isNotificationsEnabled;
        private int _selectedThemeIndex;
        private int _selectedLanguageIndex;
        private bool _isCheckingForUpdates;

        public SettingsViewModel()
        {
            LoadAppVersion();
            LoadSettings();
            CheckForUpdatesCommand = new RelayCommand(async _ => await CheckForUpdates(), _ => CanCheckForUpdates());
        }

        public bool IsNotificationsEnabled
        {
            get => _isNotificationsEnabled;
            set
            {
                _isNotificationsEnabled = value;
                ApplicationData.Current.LocalSettings.Values["notifications"] = value;
                OnPropertyChanged();
            }
        }

        public int SelectedThemeIndex
        {
            get => _selectedThemeIndex;
            set
            {
                _selectedThemeIndex = value;
                ApplyTheme(value);
                OnPropertyChanged();
            }
        }

        public int SelectedLanguageIndex
        {
            get => _selectedLanguageIndex;
            set
            {
                _selectedLanguageIndex = value;
                ApplyLanguage(value);
                OnPropertyChanged();
            }
        }

        public bool IsCheckingForUpdates
        {
            get => _isCheckingForUpdates;
            set
            {
                _isCheckingForUpdates = value;
                OnPropertyChanged();
                ((RelayCommand)CheckForUpdatesCommand).RaiseCanExecuteChanged();
            }
        }

        private void LoadAppVersion()
        {
            try
            {
                var version = Package.Current.Id.Version;
                AppVersion = $"Version: {version.Major}.{version.Minor}.{version.Build}.{version.Revision}";
            }
            catch (Exception)
            {
                AppVersion = "Version: N/A (Not Packaged)";
            }
        }

        private void LoadSettings()
        {
            IsNotificationsEnabled = ApplicationData.Current.LocalSettings.Values["notifications"] as bool? ?? false;

            var savedTheme = ApplicationData.Current.LocalSettings.Values["theme"] as string;
            _selectedThemeIndex = savedTheme switch
            {
                "Light" => 0,
                "Dark" => 1,
                _ => 2,
            };

            var savedLang = ApplicationData.Current.LocalSettings.Values["language"] as string;
            _selectedLanguageIndex = savedLang == "pt-BR" ? 0 : 1;
        }

        private void ApplyTheme(int index)
        {
            var theme = index switch
            {
                0 => ElementTheme.Light,
                1 => ElementTheme.Dark,
                _ => ElementTheme.Default,
            };
            var themeSetting = index switch
            {
                0 => "Light",
                1 => "Dark",
                _ => "Default",
            };

            if (App.m_window.Content is FrameworkElement rootElement)
            {
                rootElement.RequestedTheme = theme;
            }
            ApplicationData.Current.LocalSettings.Values["theme"] = themeSetting;
        }

        private void ApplyLanguage(int index)
        {
            var lang = index == 0 ? "pt-BR" : "en-US";
            ApplicationData.Current.LocalSettings.Values["language"] = lang;
        }

        private bool CanCheckForUpdates()
        {
            if (IsCheckingForUpdates) return false;

            try
            {
                var package = Package.Current;
                return true;
            }
            catch (Exception)
            {
                return false;
            }
        }

        private async Task CheckForUpdates()
        {
            IsCheckingForUpdates = true;

            try
            {
                var manager = AppInstallerManager.GetDefault();
                var result = await manager.CheckForUpdateAsync();

                switch (result.Availability)
                {
                    case AppInstallerUpdateAvailability.Available:
                    case AppInstallerUpdateAvailability.Required:
                        await WindowService.ShowContentDialogAsync("Update Found", "A new version is available and will be downloaded. The app will restart after installation.");
                        await manager.TryUpdateAndRestartAsync();
                        break;
                    case AppInstallerUpdateAvailability.NoUpdates:
                        await WindowService.ShowContentDialogAsync("No Updates", "You are already on the latest version.");
                        break;
                    case AppInstallerUpdateAvailability.Disabled:
                        await WindowService.ShowContentDialogAsync("Updates Disabled", "Automatic updates have been disabled by an administrator.");
                        break;
                    case AppInstallerUpdateAvailability.Error:
                    default:
                        await WindowService.ShowContentDialogAsync("Error", "Could not check for updates. Please check your internet connection.");
                        break;
                }
            }
            catch (Exception ex)
            {
                await WindowService.ShowContentDialogAsync("Error", $"An error occurred while checking for updates: {ex.Message}");
            }
            finally
            {
                IsCheckingForUpdates = false;
            }
        }

        public event PropertyChangedEventHandler PropertyChanged;
        protected void OnPropertyChanged([CallerMemberName] string propertyName = null)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }
    }
}