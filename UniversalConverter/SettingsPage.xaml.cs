using Microsoft.UI.Xaml.Controls;
using System;
using Windows.ApplicationModel;

namespace UniversalConverter
{
    public sealed partial class SettingsPage : Page
    {
        public SettingsPage()
        {
            this.InitializeComponent();
            LoadAppVersion();
            CheckForUpdatesButton.Click += CheckForUpdatesButton_Click;
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

        private async void CheckForUpdatesButton_Click(object sender, Microsoft.UI.Xaml.RoutedEventArgs e)
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