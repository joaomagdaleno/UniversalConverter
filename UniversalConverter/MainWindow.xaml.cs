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

        public void NavigateToPage(Type pageType)
        {
            ContentFrame.Navigate(pageType);
        }

        public void NavigateToPageWithParameter(Type pageType, object parameter)
        {
            ContentFrame.Navigate(pageType, parameter);
        }

        private void NavView_ItemInvoked(NavigationView sender, NavigationViewItemInvokedEventArgs args)
        {
            if (args.IsSettingsInvoked)
            {
                NavigateToPage(typeof(SettingsPage));
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
                            NavigateToPage(typeof(DashboardPage));
                            break;
                        case "ConverterPage":
                            NavigateToPage(typeof(ConverterPage));
                            break;
                        case "QueuePage":
                            NavigateToPage(typeof(QueuePage));
                            break;
                    }
                }
            }
        }
    }
}