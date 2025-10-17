using Microsoft.UI.Xaml.Controls;

namespace UniversalConverter
{
    public sealed partial class SettingsPage : Page
    {
        public SettingsViewModel ViewModel { get; private set; }

        public SettingsPage()
        {
            this.InitializeComponent();
            ViewModel = AppServices.Services.GetRequiredService<SettingsViewModel>();
            ViewModel.WindowService = AppServices.Services.GetRequiredService<IWindowService>();
            this.DataContext = ViewModel;
        }
    }
}