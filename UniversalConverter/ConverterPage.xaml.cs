using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media.Imaging;
using System;
using System.IO;
using Windows.Storage;
using Windows.Storage.Pickers;
using WinRT.Interop;

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
            WebpQualitySlider.IsEnabled = selectedFormat == "WEBP";
            GifLoopCheckBox.IsEnabled = selectedFormat == "GIF";
        }

        private async void SelectFileButton_Click(object sender, Microsoft.UI.Xaml.RoutedEventArgs e)
        {
            var fileOpenPicker = new FileOpenPicker();
            fileOpenPicker.FileTypeFilter.Add(".webp");
            fileOpenPicker.FileTypeFilter.Add(".gif");

            var window = App.Current.Windows[0];
            InitializeWithWindow.Initialize(fileOpenPicker, window.GetWindowHandle());

            selectedFile = await fileOpenPicker.PickSingleFileAsync();

            if (selectedFile != null)
            {
                PreviewTextBlock.Visibility = Microsoft.UI.Xaml.Visibility.Collapsed;
                PreviewImage.Source = new BitmapImage(new Uri(selectedFile.Path));
                ConvertButton.IsEnabled = true;

                // Auto-select output format
                if (Path.GetExtension(selectedFile.Name).ToLower() == ".webp")
                {
                    OutputFormatComboBox.SelectedItem = OutputFormatComboBox.Items[0]; // GIF
                }
                else
                {
                    OutputFormatComboBox.SelectedItem = OutputFormatComboBox.Items[1]; // WEBP
                }
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
                    GifRepeatCount = GifLoopCheckBox.IsChecked == true ? (ushort)0 : (ushort)1
                };

                try
                {
                    if (selectedFormat == "GIF")
                    {
                        imageConverter.ConvertWebPToGif(selectedFile.Path, destinationFile.Path, options);
                    }
                    else
                    {
                        imageConverter.ConvertGifToWebP(selectedFile.Path, destinationFile.Path, options);
                    }
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
                    GifRepeatCount = GifLoopCheckBox.IsChecked == true ? (ushort)0 : (ushort)1
                };

                string inputExtension = selectedFormat == "GIF" ? ".webp" : ".gif";

                foreach (var file in files)
                {
                    if (Path.GetExtension(file.Name).ToLower() == inputExtension)
                    {
                        try
                        {
                            string newFileName = Path.GetFileNameWithoutExtension(file.Name) + $".{selectedFormat.ToLower()}";
                            StorageFile newFile = await folder.CreateFileAsync(newFileName, CreationCollisionOption.GenerateUniqueName);

                            if (selectedFormat == "GIF")
                            {
                                imageConverter.ConvertWebPToGif(file.Path, newFile.Path, options);
                            }
                            else
                            {
                                imageConverter.ConvertGifToWebP(file.Path, newFile.Path, options);
                            }
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