using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media.Imaging;
using System;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using Windows.ApplicationModel.DataTransfer;
using Windows.Storage;
using Windows.Storage.Pickers;
using Windows.Storage.Streams;
using WinRT.Interop;
using SixLabors.ImageSharp.Formats.Png;
using System.Collections.ObjectModel;
using SixLabors.ImageSharp.Processing;
using Microsoft.UI.Xaml.Navigation;

namespace UniversalConverter
{
    public sealed partial class ConverterPage : Page
    {
        private StorageFile selectedFile;
        private readonly ImageConverter imageConverter = new ImageConverter();
        private readonly ObservableCollection<ConversionPreset> Presets = new ObservableCollection<ConversionPreset>();
        private bool _isPresetBeingApplied = false;
        private RotateMode _currentRotation = RotateMode.None;

        public ConverterPage()
        {
            this.InitializeComponent();
            SetupEventHandlers();
            PresetComboBox.ItemsSource = Presets;
            Loaded += async (s, e) => await LoadPresetsAsync();
        }

        private void SetupEventHandlers()
        {
            SelectFileButton.Click += SelectFileButton_Click;
            SelectFolderButton.Click += SelectFolderButton_Click;
            ConvertButton.Click += ConvertButton_Click;
            this.DragLeave += (s, e) => DragDropOverlay.Visibility = Visibility.Collapsed;
            ConvertButton.IsEnabled = false;

            PresetComboBox.SelectionChanged += PresetComboBox_SelectionChanged;
            SavePresetButton.Click += SavePresetButton_Click;
            DeletePresetButton.Click += DeletePresetButton_Click;

            OutputFormatComboBox.SelectionChanged += Option_Changed;
            WebpQualitySlider.ValueChanged += Option_Changed;
            JpgQualitySlider.ValueChanged += Option_Changed;
            PngCompressionSlider.ValueChanged += Option_Changed;
            GifLoopCheckBox.Click += Option_Changed;
            WidthNumberBox.LostFocus += Option_Changed;
            HeightNumberBox.LostFocus += Option_Changed;
            AspectRatioCheckBox.Click += Option_Changed;
            RotateLeftButton.Click += RotateLeftButton_Click;
            RotateRightButton.Click += RotateRightButton_Click;

            UpdateOptionsUI();
        }

        private void RotateLeftButton_Click(object sender, RoutedEventArgs e)
        {
            _currentRotation = GetNewRotation(RotateMode.Rotate270);
            UpdatePreviewAsync().AsTask();
        }

        private void RotateRightButton_Click(object sender, RoutedEventArgs e)
        {
            _currentRotation = GetNewRotation(RotateMode.Rotate90);
            UpdatePreviewAsync().AsTask();
        }

        private RotateMode GetNewRotation(RotateMode rotation)
        {
            if (rotation == RotateMode.Rotate90) // Rotate Right
            {
                switch (_currentRotation)
                {
                    case RotateMode.None:
                        return RotateMode.Rotate90;
                    case RotateMode.Rotate90:
                        return RotateMode.Rotate180;
                    case RotateMode.Rotate180:
                        return RotateMode.Rotate270;
                    case RotateMode.Rotate270:
                    default:
                        return RotateMode.None;
                }
            }
            else if (rotation == RotateMode.Rotate270) // Rotate Left
            {
                switch (_currentRotation)
                {
                    case RotateMode.None:
                        return RotateMode.Rotate270;
                    case RotateMode.Rotate270:
                        return RotateMode.Rotate180;
                    case RotateMode.Rotate180:
                        return RotateMode.Rotate90;
                    case RotateMode.Rotate90:
                    default:
                        return RotateMode.None;
                }
            }
            return _currentRotation; // Should not happen
        }

        private async Task LoadPresetsAsync()
        {
            Presets.Clear();
            foreach (var preset in PresetService.Presets)
            {
                Presets.Add(preset);
            }
        }

        private void PresetComboBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (PresetComboBox.SelectedItem is ConversionPreset selectedPreset)
            {
                _isPresetBeingApplied = true;
                ApplyPreset(selectedPreset.Options);
                _isPresetBeingApplied = false;
                UpdatePreviewAsync().AsTask();
            }
        }

        private void ApplyPreset(ConversionOptions options)
        {
            _currentRotation = options.Rotate;
            WebpQualitySlider.Value = options.WebpQuality;
            JpgQualitySlider.Value = options.JpgQuality;
            PngCompressionSlider.Value = (int)options.PngCompression;
            GifLoopCheckBox.IsChecked = options.GifRepeatCount == 0;
            WidthNumberBox.Value = options.Width;
            HeightNumberBox.Value = options.Height;
            AspectRatioCheckBox.IsChecked = options.KeepAspectRatio;
        }

        private async void SavePresetButton_Click(object sender, RoutedEventArgs e)
        {
            var nameTextBox = new TextBox { PlaceholderText = "Nome do Perfil" };
            var dialog = new ContentDialog { Title = "Salvar Perfil", Content = nameTextBox, PrimaryButtonText = "Salvar", CloseButtonText = "Cancelar", XamlRoot = this.XamlRoot };
            var result = await dialog.ShowAsync();
            if (result == ContentDialogResult.Primary && !string.IsNullOrWhiteSpace(nameTextBox.Text))
            {
                var newPreset = new ConversionPreset { Name = nameTextBox.Text, Options = GetCurrentConversionOptions() };
                await PresetService.AddPresetAsync(newPreset);
                await LoadPresetsAsync();
                PresetComboBox.SelectedItem = Presets.FirstOrDefault(p => p.Name == newPreset.Name);
            }
        }

        private async void DeletePresetButton_Click(object sender, RoutedEventArgs e)
        {
            if (PresetComboBox.SelectedItem is ConversionPreset selectedPreset)
            {
                await PresetService.DeletePresetAsync(selectedPreset.Name);
                await LoadPresetsAsync();
            }
        }

        private async void Option_Changed(object sender, object e)
        {
            if (_isPresetBeingApplied) return;
            if (sender is ComboBox) UpdateOptionsUI();
            await UpdatePreviewAsync();
        }

        private async Task UpdatePreviewAsync()
        {
            if (selectedFile == null) return;
            var options = GetCurrentConversionOptions();
            var selectedFormat = (OutputFormatComboBox.SelectedItem as ComboBoxItem)?.Content.ToString();
            if (string.IsNullOrEmpty(selectedFormat)) return;
            try
            {
                using (var stream = imageConverter.ConvertImageToStream(selectedFile.Path, $".{selectedFormat.ToLower()}", options))
                {
                    var bitmapImage = new BitmapImage();
                    await bitmapImage.SetSourceAsync(stream.AsRandomAccessStream());
                    ConvertedPreviewImage.Source = bitmapImage;
                }
            }
            catch { ConvertedPreviewImage.Source = null; }
        }

        private void Page_DragOver(object sender, DragEventArgs e)
        {
            e.AcceptedOperation = DataPackageOperation.Copy;
            if (e.DataView.Contains(StandardDataFormats.StorageItems)) DragDropOverlay.Visibility = Visibility.Visible;
        }

        private async void Page_Drop(object sender, DragEventArgs e)
        {
            DragDropOverlay.Visibility = Visibility.Collapsed;
            if (e.DataView.Contains(StandardDataFormats.StorageItems))
            {
                var items = await e.DataView.GetStorageItemsAsync();
                if (items.Any())
                {
                    if (items[0] is StorageFile file) await HandleDroppedFile(file);
                    else if (items[0] is StorageFolder folder) await HandleDroppedFolder(folder);
                }
            }
        }

        private async Task HandleDroppedFile(StorageFile file)
        {
            selectedFile = file;
            _currentRotation = RotateMode.None;
            PreviewTextBlock.Visibility = Visibility.Collapsed;
            OriginalPreviewImage.Source = new BitmapImage(new Uri(file.Path));
            ConvertButton.IsEnabled = true;
            await UpdatePreviewAsync();
        }

        private async Task HandleDroppedFolder(StorageFolder sourceFolder)
        {
            var destinationPicker = new FolderPicker { SuggestedStartLocation = PickerLocationId.PicturesLibrary };
            InitializeWithWindow.Initialize(destinationPicker, App.m_window.GetWindowHandle());
            StorageFolder destinationFolder = await destinationPicker.PickSingleFolderAsync();
            if (destinationFolder != null)
            {
                await ProcessBatchConversion(sourceFolder, destinationFolder);
            }
        }

        private void UpdateOptionsUI()
        {
            var selectedFormat = (OutputFormatComboBox.SelectedItem as ComboBoxItem)?.Content.ToString();
            WebpQualitySlider.Visibility = selectedFormat == "WEBP" ? Visibility.Visible : Visibility.Collapsed;
            JpgQualitySlider.Visibility = selectedFormat == "JPG" ? Visibility.Visible : Visibility.Collapsed;
            PngCompressionSlider.Visibility = selectedFormat == "PNG" ? Visibility.Visible : Visibility.Collapsed;
            GifLoopCheckBox.Visibility = selectedFormat == "GIF" ? Visibility.Visible : Visibility.Collapsed;
        }

        private async void SelectFileButton_Click(object sender, RoutedEventArgs e)
        {
            var fileOpenPicker = new FileOpenPicker { FileTypeFilter = { ".webp", ".gif", ".jpg", ".jpeg", ".png" } };
            InitializeWithWindow.Initialize(fileOpenPicker, App.m_window.GetWindowHandle());
            var file = await fileOpenPicker.PickSingleFileAsync();
            if (file != null) await HandleDroppedFile(file);
        }

        private async void ConvertButton_Click(object sender, RoutedEventArgs e)
        {
            if (selectedFile == null) return;
            var selectedFormat = (OutputFormatComboBox.SelectedItem as ComboBoxItem)?.Content.ToString();
            if (string.IsNullOrEmpty(selectedFormat))
            {
                await ShowContentDialog("Formato Inválido", "Por favor, selecione um formato de saída.");
                return;
            }

            var fileSavePicker = new FileSavePicker { SuggestedStartLocation = PickerLocationId.PicturesLibrary, SuggestedFileName = Path.GetFileNameWithoutExtension(selectedFile.Name) };
            fileSavePicker.FileTypeChoices.Add($"{selectedFormat} Image", new[] { $".{selectedFormat.ToLower()}" });
            InitializeWithWindow.Initialize(fileSavePicker, App.m_window.GetWindowHandle());

            StorageFile destinationFile = await fileSavePicker.PickSaveFileAsync();
            if (destinationFile != null)
            {
                try
                {
                    imageConverter.ConvertImage(selectedFile.Path, destinationFile.Path, GetCurrentConversionOptions());
                    await StatsService.RecordConversion();
                    await ShowContentDialog("Sucesso", "A imagem foi convertida com sucesso!");
                }
                catch (Exception ex) { await ShowContentDialog("Erro", $"Ocorreu um erro: {ex.Message}"); }
            }
        }

        private async void SelectFolderButton_Click(object sender, RoutedEventArgs e)
        {
            var sourcePicker = new FolderPicker { SuggestedStartLocation = PickerLocationId.PicturesLibrary };
            InitializeWithWindow.Initialize(sourcePicker, App.m_window.GetWindowHandle());
            StorageFolder sourceFolder = await sourcePicker.PickSingleFolderAsync();
            if (sourceFolder != null)
            {
                await HandleDroppedFolder(sourceFolder);
            }
        }

        private async Task ProcessBatchConversion(StorageFolder sourceFolder, StorageFolder destinationFolder)
        {
            var selectedFormat = (OutputFormatComboBox.SelectedItem as ComboBoxItem)?.Content.ToString();
            if (string.IsNullOrEmpty(selectedFormat))
            {
                await ShowContentDialog("Formato Inválido", "Por favor, selecione um formato de saída.");
                return;
            }

            QueueService.ClearQueue();
            await AddFolderToQueueRecursively(sourceFolder, sourceFolder, destinationFolder, selectedFormat);

            var mainWindow = App.m_window as MainWindow;
            mainWindow?.NavigateToPage(typeof(QueuePage));
        }

        private async Task AddFolderToQueueRecursively(StorageFolder currentFolder, StorageFolder rootSourceFolder, StorageFolder currentDestinationFolder, string outputFormat)
        {
            var items = await currentFolder.GetItemsAsync();
            foreach (var item in items)
            {
                if (item is StorageFolder subFolder && KeepStructureCheckBox.IsChecked == true)
                {
                    var newDestFolder = await currentDestinationFolder.CreateFolderAsync(subFolder.Name, CreationCollisionOption.OpenIfExists);
                    await AddFolderToQueueRecursively(subFolder, rootSourceFolder, newDestFolder, outputFormat);
                }
                else if (item is StorageFile file)
                {
                    var validExtensions = new[] { ".webp", ".gif", ".jpg", ".jpeg", ".png" };
                    string inputExtension = Path.GetExtension(file.Name).ToLower();
                    string outputExtension = $".{outputFormat.ToLower()}";

                    if (validExtensions.Contains(inputExtension) && inputExtension != outputExtension)
                    {
                        string newFileName = Path.ChangeExtension(file.Name, outputExtension);

                        var queueItem = new QueueItem
                        {
                            SourcePath = file.Path,
                            DestinationPath = Path.Combine(currentDestinationFolder.Path, newFileName),
                            Options = GetCurrentConversionOptions(),
                            Status = QueueStatus.Pending
                        };
                        QueueService.AddToQueue(queueItem);
                    }
                }
            }
        }

        private ConversionOptions GetCurrentConversionOptions()
        {
            return new ConversionOptions
            {
                WebpQuality = (int)WebpQualitySlider.Value,
                GifRepeatCount = GifLoopCheckBox.IsChecked == true ? (ushort)0 : (ushort)1,
                JpgQuality = (int)JpgQualitySlider.Value,
                PngCompression = (PngCompressionLevel)Convert.ToInt32(PngCompressionSlider.Value),
                Width = (int)WidthNumberBox.Value,
                Height = (int)HeightNumberBox.Value,
                KeepAspectRatio = AspectRatioCheckBox.IsChecked == true,
                Rotate = _currentRotation
            };
        }

        private async Task ShowContentDialog(string title, string content)
        {
            var dialog = new ContentDialog { Title = title, Content = content, CloseButtonText = "Ok", XamlRoot = this.XamlRoot };
            await dialog.ShowAsync();
        }

        protected override async void OnNavigatedTo(NavigationEventArgs e)
        {
            base.OnNavigatedTo(e);
            if (e.Parameter is StorageFile file)
            {
                await HandleDroppedFile(file);
            }
        }
    }
}