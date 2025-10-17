using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Navigation;
using System;
using System.Threading.Tasks;
using Windows.ApplicationModel.DataTransfer;
using Windows.Storage;

namespace UniversalConverter
{
    public sealed partial class ConverterPage : Page
    {
        public ConverterViewModel ViewModel { get; private set; }

        public ConverterPage()
        {
            this.InitializeComponent();
            ViewModel = new ConverterViewModel();
            this.DataContext = ViewModel;
        }

        protected override async void OnNavigatedTo(NavigationEventArgs e)
        {
            base.OnNavigatedTo(e);
            try
            {
                if (e.Parameter is IStorageItem item)
                {
                    await ViewModel.HandleDroppedFileAsync(item);
                }
            }
            catch (Exception ex)
            {
                await ShowContentDialog("Error", $"An unexpected error occurred: {ex.Message}");
            }
        }

        private void Page_DragOver(object sender, Microsoft.UI.Xaml.DragEventArgs e)
        {
            e.AcceptedOperation = DataPackageOperation.Copy;
        }

        private async void Page_Drop(object sender, Microsoft.UI.Xaml.DragEventArgs e)
        {
            try
            {
                if (e.DataView.Contains(StandardDataFormats.StorageItems))
                {
                    var items = await e.DataView.GetStorageItemsAsync();
                    if (items.Count > 0)
                    {
                        await ViewModel.HandleDroppedFileAsync(items[0]);
                    }
                }
            }
            catch (Exception ex)
            {
                await ShowContentDialog("Error", $"An error occurred during drop: {ex.Message}");
            }
        }

        private async Task ShowContentDialog(string title, string content)
        {
            var dialog = new ContentDialog { Title = title, Content = content, CloseButtonText = "Ok", XamlRoot = this.XamlRoot };
            await dialog.ShowAsync();
        }
    }
}