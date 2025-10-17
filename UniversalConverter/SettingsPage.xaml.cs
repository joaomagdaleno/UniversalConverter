using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using System;
using Windows.ApplicationModel;
using Windows.Storage;

namespace UniversalConverter
{
    public sealed partial class SettingsPage : Page
    {
        public SettingsPage()
        {
            this.InitializeComponent();
            LoadAppVersion();
            CheckForUpdatesButton.Click += CheckForUpdatesButton_Click;
            ThemeComboBox.SelectionChanged += ThemeComboBox_SelectionChanged;
            LanguageComboBox.SelectionChanged += LanguageComboBox_SelectionChanged;
            LoadThemeSetting();
            LoadLanguageSetting();
        }

        private void LanguageComboBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            var selectedLang = (LanguageComboBox.SelectedItem as ComboBoxItem)?.Tag?.ToString();
            if (selectedLang != null)
            {
                ApplicationData.Current.LocalSettings.Values["language"] = selectedLang;
                ShowContentDialog("Idioma Alterado", "A alteração do idioma terá efeito na próxima vez que você iniciar o aplicativo.").AsTask();
            }
        }

        private void LoadLanguageSetting()
        {
            var savedLang = ApplicationData.Current.LocalSettings.Values["language"] as string;
            if (savedLang != null)
            {
                var index = savedLang == "pt-BR" ? 0 : 1;
                LanguageComboBox.SelectedIndex = index;
            }
            else
            {
                LanguageComboBox.SelectedIndex = 0; // Padrão Português
            }
        }

        private void LoadThemeSetting()
        {
            var savedTheme = ApplicationData.Current.LocalSettings.Values["theme"] as string;
            if (savedTheme != null)
            {
                var index = savedTheme switch
                {
                    "Light" => 0,
                    "Dark" => 1,
                    _ => 2,
                };
                ThemeComboBox.SelectedIndex = index;
            }
            else
            {
                ThemeComboBox.SelectedIndex = 2; // Default to System
            }
        }

        private void ThemeComboBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            var selectedItem = (ThemeComboBox.SelectedItem as ComboBoxItem)?.Content.ToString();
            ElementTheme theme;
            string themeSetting;

            switch (selectedItem)
            {
                case "Claro":
                    theme = ElementTheme.Light;
                    themeSetting = "Light";
                    break;
                case "Escuro":
                    theme = ElementTheme.Dark;
                    themeSetting = "Dark";
                    break;
                default:
                    theme = ElementTheme.Default;
                    themeSetting = "Default";
                    break;
            }

            if (App.m_window.Content is FrameworkElement rootElement)
            {
                rootElement.RequestedTheme = theme;
            }
            ApplicationData.Current.LocalSettings.Values["theme"] = themeSetting;
        }

        private void LoadAppVersion()
        {
            try
            {
                var version = Package.Current.Id.Version;
                VersionTextBlock.Text = $"Versão: {version.Major}.{version.Minor}.{version.Build}.{version.Revision}";
            }
            catch (Exception)
            {
                VersionTextBlock.Text = "Versão: N/A (Não empacotado)";
                CheckForUpdatesButton.IsEnabled = false;
            }
        }

        private async void CheckForUpdatesButton_Click(object sender, RoutedEventArgs e)
        {
            CheckForUpdatesButton.IsEnabled = false;
            CheckForUpdatesButton.Content = "Verificando...";

            try
            {
                var manager = AppInstallerManager.GetDefault();
                var result = await manager.CheckForUpdateAsync();

                switch (result.Availability)
                {
                    case AppInstallerUpdateAvailability.Available:
                    case AppInstallerUpdateAvailability.Required:
                        await ShowContentDialog("Atualização encontrada", "Uma nova versão está disponível e será baixada. O aplicativo será reiniciado após a instalação.");
                        await manager.TryUpdateAndRestartAsync();
                        break;
                    case AppInstallerUpdateAvailability.NoUpdates:
                        await ShowContentDialog("Nenhuma atualização", "Você já está com a versão mais recente.");
                        break;
                    case AppInstallerUpdateAvailability.Disabled:
                        await ShowContentDialog("Atualizações desabilitadas", "As atualizações automáticas foram desabilitadas pelo administrador.");
                        break;
                    case AppInstallerUpdateAvailability.Error:
                    default:
                        await ShowContentDialog("Erro", "Não foi possível verificar por atualizações. Verifique sua conexão com a internet.");
                        break;
                }
            }
            catch (Exception ex)
            {
                await ShowContentDialog("Erro", $"Ocorreu um erro ao verificar por atualizações: {ex.Message}");
            }
            finally
            {
                CheckForUpdatesButton.IsEnabled = true;
                CheckForUpdatesButton.Content = "Verificar Atualizações";
            }
        }

        private async System.Threading.Tasks.Task ShowContentDialog(string title, string content)
        {
            ContentDialog dialog = new ContentDialog
            {
                Title = title,
                Content = content,
                CloseButtonText = "Ok",
                XamlRoot = this.XamlRoot
            };
            await dialog.ShowAsync();
        }
    }
}