using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media.Imaging;
using System;
using System.IO;
using System.Linq;
using Windows.Storage;
using Windows.Storage.Pickers;
using WinRT.Interop;
using SixLabors.ImageSharp.Formats.Png;

namespace UniversalConverter
{
    public sealed partial class ConverterPage : Page
    {
        private StorageFile selectedFile;
        private readonly ImageConverter imageConverter = new ImageConverter();

        public ConverterPage()
        {
            this.InitializeComponent();
            SelectFileButton.Click += SelectFileButton_Click;
            SelectFolderButton.Click += SelectFolderButton_Click;
            ConvertButton.Click += ConvertButton_Click;
            OutputFormatComboBox.SelectionChanged += OutputFormatComboBox_SelectionChanged;

            ConvertButton.IsEnabled = false;
            UpdateOptionsUI();
        }

        private void UpdateOptionsUI()
        {
            var selectedFormat = (OutputFormatComboBox.SelectedItem as ComboBoxItem)?.Content.ToString();
            WebpQualitySlider.Visibility = selectedFormat == "WEBP" ? Microsoft.UI.Xaml.Visibility.Visible : Microsoft.UI.Xaml.Visibility.Collapsed;
            JpgQualitySlider.Visibility = selectedFormat == "JPG" ? Microsoft.UI.Xaml.Visibility.Visible : Microsoft.UI.Xaml.Visibility.Collapsed;
            PngCompressionSlider.Visibility = selectedFormat == "PNG" ? Microsoft.UI.Xaml.Visibility.Visible : Microsoft.UI.Xaml.Visibility.Collapsed;
            GifLoopCheckBox.Visibility = selectedFormat == "GIF" ? Microsoft.UI.Xaml.Visibility.Visible : Microsoft.UI.Xaml.Visibility.Collapsed;
        }

        private async void SelectFileButton_Click(object sender, Microsoft.UI.Xaml.RoutedEventArgs e)
        {
            var fileOpenPicker = new FileOpenPicker();
            fileOpenPicker.FileTypeFilter.Add(".webp");
            fileOpenPicker.FileTypeFilter.Add(".gif");
            fileOpenPicker.FileTypeFilter.Add(".jpg");
            fileOpenPicker.FileTypeFilter.Add(".jpeg");
            fileOpenPicker.FileTypeFilter.Add(".png");

            var window = App.Current.Windows[0];
            InitializeWithWindow.Initialize(fileOpenPicker, window.GetWindowHandle());

            selectedFile = await fileOpenPicker.PickSingleFileAsync();

            if (selectedFile != null)
            {
                PreviewTextBlock.Visibility = Microsoft.UI.Xaml.Visibility.Collapsed;
                PreviewImage.Source = new BitmapImage(new Uri(selectedFile.Path));
                ConvertButton.IsEnabled = true;
            }
        }

        private async void ConvertButton_Click(object sender, Microsoft.UI.Xaml.RoutedEventArgs e)
        {
            if (selectedFile == null) return;
            var selectedFormat = (OutputFormatComboBox.SelectedItem as ComboBoxItem)?.Content.ToString();
            if (string.IsNullOrEmpty(selectedFormat))
            {
                await ShowContentDialog("Formato Inválido", "Por favor, selecione um formato de saída.");
                return;
            }

            var fileSavePicker = new FileSavePicker();
            fileSavePicker.SuggestedStartLocation = PickerLocationId.PicturesLibrary;
            fileSavePicker.FileTypeChoices.Add($"{selectedFormat} Image", new[] { $".{selectedFormat.ToLower()}" });
            fileSavePicker.SuggestedFileName = Path.GetFileNameWithoutExtension(selectedFile.Name);

            var window = App.Current.Windows[0];
            InitializeWithWindow.Initialize(fileSavePicker, window.GetWindowHandle());

            StorageFile destinationFile = await fileSavePicker.PickSaveFileAsync();

            if (destinationFile != null)
            {
                var options = new ConversionOptions
                {
                    WebpQuality = (int)WebpQualitySlider.Value,
                    GifRepeatCount = GifLoopCheckBox.IsChecked == true ? (ushort)0 : (ushort)1,
                    JpgQuality = (int)JpgQualitySlider.Value,
                    PngCompression = (PngCompressionLevel)Convert.ToInt32(PngCompressionSlider.Value)
                };

                try
                {
                    imageConverter.ConvertImage(selectedFile.Path, destinationFile.Path, options);
                    StatsService.RecordConversion();
                    await ShowContentDialog("Sucesso", "A imagem foi convertida com sucesso!");
                }
                catch (Exception ex)
                {
                    await ShowContentDialog("Erro", $"Ocorreu um erro durante a conversão: {ex.Message}");
                }
            }
        }

        private async void SelectFolderButton_Click(object sender, Microsoft.UI.Xaml.RoutedEventArgs e)
        {
            var selectedFormat = (OutputFormatComboBox.SelectedItem as ComboBoxItem)?.Content.ToString();
            if (string.IsNullOrEmpty(selectedFormat))
            {
                await ShowContentDialog("Formato Inválido", "Por favor, selecione um formato de saída para a conversão em lote.");
                return;
            }

            var folderPicker = new FolderPicker();
            folderPicker.SuggestedStartLocation = PickerLocationId.PicturesLibrary;
            folderPicker.FileTypeFilter.Add("*");

            var window = App.Current.Windows[0];
            InitializeWithWindow.Initialize(folderPicker, window.GetWindowHandle());

            StorageFolder folder = await folderPicker.PickSingleFolderAsync();
            if (folder != null)
            {
                var files = await folder.GetFilesAsync();
                int successCount = 0;
                int failCount = 0;

                var options = new ConversionOptions
                {
                    WebpQuality = (int)WebpQualitySlider.Value,
                    GifRepeatCount = GifLoopCheckBox.IsChecked == true ? (ushort)0 : (ushort)1,
                    JpgQuality = (int)JpgQualitySlider.Value,
                    PngCompression = (PngCompressionLevel)Convert.ToInt32(PngCompressionSlider.Value)
                };

                var validExtensions = new[] { ".webp", ".gif", ".jpg", ".jpeg", ".png" };
                string outputExtension = $".{selectedFormat.ToLower()}";

                foreach (var file in files)
                {
                    string inputExtension = Path.GetExtension(file.Name).ToLower();
                    if (validExtensions.Contains(inputExtension) && inputExtension != outputExtension)
                    {
                        try
                        {
                            string newFileName = Path.GetFileNameWithoutExtension(file.Name) + outputExtension;
                            StorageFile newFile = await folder.CreateFileAsync(newFileName, CreationCollisionOption.GenerateUniqueName);

                            imageConverter.ConvertImage(file.Path, newFile.Path, options);
                            StatsService.RecordConversion();
                            successCount++;
                        }
                        catch
                        {
                            failCount++;
                        }
                    }
                }
                await ShowContentDialog("Conversão em Lote Concluída", $"{successCount} arquivos convertidos com sucesso.\n{failCount} falhas.");
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

        private void OutputFormatComboBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            UpdateOptionsUI();
        }
    }
}