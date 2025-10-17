using Microsoft.UI.Xaml.Controls;

namespace UniversalConverter
{
    public sealed partial class QueuePage : Page
    {
        public QueueViewModel ViewModel { get; private set; }

        public QueuePage()
        {
            this.InitializeComponent();
            ViewModel = AppServices.Services.GetRequiredService<QueueViewModel>();
            ViewModel.Initialize(this.DispatcherQueue);
            this.DataContext = ViewModel;
        }
    }
}