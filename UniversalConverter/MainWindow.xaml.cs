using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;

namespace UniversalConverter
{
    public sealed partial class MainWindow : Window
    {
        public MainWindow()
        {
            this.InitializeComponent();
            this.Title = "Universal Converter";
            NavView.SelectedItem = NavView.MenuItems[0];
            ContentFrame.Navigate(typeof(DashboardPage));
        }

        private void NavView_ItemInvoked(NavigationView sender, NavigationViewItemInvokedEventArgs args)
        {
            if (args.IsSettingsInvoked)
            {
                ContentFrame.Navigate(typeof(SettingsPage));
            }
            else
            {
                var item = args.InvokedItemContainer as NavigationViewItem;
                if (item != null)
                {
                    var tag = item.Tag.ToString();
                    switch (tag)
                    {
                        case "DashboardPage":
                            ContentFrame.Navigate(typeof(DashboardPage));
                            break;
                        case "ConverterPage":
                            ContentFrame.Navigate(typeof(ConverterPage));
                            break;
                    }
                }
            }
        }
    }
}