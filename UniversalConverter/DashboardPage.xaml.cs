using Microsoft.UI.Xaml.Controls;

namespace UniversalConverter
{
    public sealed partial class DashboardPage : Page
    {
        public DashboardViewModel ViewModel { get; private set; }

        public DashboardPage()
        {
            this.InitializeComponent();
            ViewModel = AppServices.Services.GetRequiredService<DashboardViewModel>();
            this.DataContext = ViewModel;
        }
    }
}