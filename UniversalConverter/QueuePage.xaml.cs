using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;

namespace UniversalConverter
{
    public sealed partial class QueuePage : Page
    {
        public QueuePage()
        {
            this.InitializeComponent();
            QueueListView.ItemsSource = QueueService.Queue;
        }

        private void StartButton_Click(object sender, RoutedEventArgs e)
        {
            QueueService.StartProcessing();
        }

        private void PauseButton_Click(object sender, RoutedEventArgs e)
        {
            QueueService.PauseProcessing();
        }

        private void ClearButton_Click(object sender, RoutedEventArgs e)
        {
            QueueService.ClearQueue();
        }
    }
}