using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Navigation;

namespace UniversalConverter
{
    public sealed partial class DashboardPage : Page
    {
        public DashboardPage()
        {
            this.InitializeComponent();
        }

        protected override void OnNavigatedTo(NavigationEventArgs e)
        {
            base.OnNavigatedTo(e);
            UpdateStats();
        }

        private void UpdateStats()
        {
            TotalConversionsTextBlock.Text = StatsService.TotalConversions.ToString();
            if (StatsService.LastConversionDate.HasValue)
            {
                LastConversionTextBlock.Text = StatsService.LastConversionDate.Value.ToString("g");
            }
            else
            {
                LastConversionTextBlock.Text = "N/A";
            }
        }
    }
}