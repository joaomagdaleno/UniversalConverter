using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media.Imaging;
using SixLabors.ImageSharp.Processing;
using System;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.IO;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Threading.Tasks;
using System.Windows.Input;
using Windows.Storage;
using Windows.Storage.Pickers;

namespace UniversalConverter
{
    public class ConverterViewModel : INotifyPropertyChanged
    {
        private readonly ImageConverter _imageConverter;
        private readonly IWindowService _windowService;
        private StorageFile _selectedFile;
        private BitmapImage _originalPreviewImage;
        private BitmapImage _convertedPreviewImage;
        private string _selectedOutputFormat = "JPG";
        private ConversionOptions _options = new ConversionOptions();
        private bool _isPresetBeingApplied;
        private ConversionPreset _selectedPreset;

        public ObservableCollection<ConversionPreset> Presets { get; } = new ObservableCollection<ConversionPreset>();

        public ICommand SelectFileCommand { get; }
        public ICommand SelectFolderCommand { get; }
        public ICommand ConvertCommand { get; }
        public ICommand SavePresetCommand { get; }
        public ICommand DeletePresetCommand { get; }
        public ICommand RotateLeftCommand { get; }
        public ICommand RotateRightCommand { get; }
        public ICommand OptionChangedCommand { get; }

        public ConverterViewModel(IWindowService windowService, ImageConverter imageConverter)
        {
            _windowService = windowService;
            _imageConverter = imageConverter;
            SelectFileCommand = new RelayCommand(async _ => await SelectFileAsync());
            SelectFolderCommand = new RelayCommand(async _ => await SelectFolderAsync());
            ConvertCommand = new RelayCommand(async _ => await ConvertFileAsync(), _ => CanConvert());
            SavePresetCommand = new RelayCommand(async _ => await SavePresetAsync());
            DeletePresetCommand = new RelayCommand(async _ => await DeletePresetAsync(), _ => SelectedPreset != null);
            RotateLeftCommand = new RelayCommand(_ => RotateImage(RotateDirection.Left));
            RotateRightCommand = new RelayCommand(_ => RotateImage(RotateDirection.Right));
            OptionChangedCommand = new RelayCommand(_ => OnOptionChanged());

            LoadPresetsAsync().AsTask();
        }

        public StorageFile SelectedFile
        {
            get => _selectedFile;
            set { _selectedFile = value; OnPropertyChanged(); ((RelayCommand)ConvertCommand).RaiseCanExecuteChanged(); }
        }

        public BitmapImage OriginalPreviewImage
        {
            get => _originalPreviewImage;
            set { _originalPreviewImage = value; OnPropertyChanged(); }
        }

        public BitmapImage ConvertedPreviewImage
        {
            get => _convertedPreviewImage;
            set { _convertedPreviewImage = value; OnPropertyChanged(); }
        }

        public string SelectedOutputFormat
        {
            get => _selectedOutputFormat;
            set { _selectedOutputFormat = value; OnPropertyChanged(); OnOptionChanged(); }
        }

        public ConversionPreset SelectedPreset
        {
            get => _selectedPreset;
            set
            {
                if (_selectedPreset != value)
                {
                    _selectedPreset = value;
                    OnPropertyChanged();
                    if (value != null) ApplyPreset(value);
                    ((RelayCommand)DeletePresetCommand).RaiseCanExecuteChanged();
                }
            }
        }

        public ConversionOptions Options
        {
            get => _options;
            set { _options = value; OnPropertyChanged(); }
        }

        public async Task HandleDroppedFileAsync(IStorageItem item)
        {
            if (item is StorageFile file)
            {
                SelectedFile = file;
                Options.Rotate = RotateMode.None;
                OriginalPreviewImage = new BitmapImage(new Uri(file.Path));
                await UpdatePreviewAsync();
            }
            else if (item is StorageFolder folder)
            {
                await ProcessBatchConversionAsync(folder);
            }
        }

        private async Task SelectFileAsync()
        {
            var fileOpenPicker = new FileOpenPicker { FileTypeFilter = { ".webp", ".gif", ".jpg", ".jpeg", ".png" } };
            _windowService.InitializeWithWindow(fileOpenPicker);
            var file = await fileOpenPicker.PickSingleFileAsync();
            if (file != null) await HandleDroppedFileAsync(file);
        }

        private async Task SelectFolderAsync()
        {
            var sourcePicker = new FolderPicker { SuggestedStartLocation = PickerLocationId.PicturesLibrary };
            _windowService.InitializeWithWindow(sourcePicker);
            StorageFolder sourceFolder = await sourcePicker.PickSingleFolderAsync();
            if (sourceFolder != null) await ProcessBatchConversionAsync(sourceFolder);
        }

        private async Task ConvertFileAsync()
        {
            var fileSavePicker = new FileSavePicker { SuggestedStartLocation = PickerLocationId.PicturesLibrary, SuggestedFileName = Path.GetFileNameWithoutExtension(SelectedFile.Name) };
            fileSavePicker.FileTypeChoices.Add($"{SelectedOutputFormat} Image", new[] { $".{SelectedOutputFormat.ToLower()}" });
            _windowService.InitializeWithWindow(fileSavePicker);

            StorageFile destinationFile = await fileSavePicker.PickSaveFileAsync();
            if (destinationFile != null)
            {
                try
                {
                    _imageConverter.ConvertImage(SelectedFile.Path, destinationFile.Path, Options);
                    await StatsService.RecordConversion();
                    await _windowService.ShowContentDialogAsync("Success", "Image converted successfully!");
                }
                catch (Exception ex) { await _windowService.ShowContentDialogAsync("Error", $"An error occurred: {ex.Message}"); }
            }
        }

        private bool CanConvert() => SelectedFile != null;

        private async Task LoadPresetsAsync()
        {
            Presets.Clear();
            await PresetService.LoadPresetsAsync();
            foreach (var preset in PresetService.Presets)
            {
                Presets.Add(preset);
            }
        }

        private void ApplyPreset(ConversionPreset preset)
        {
            _isPresetBeingApplied = true;
            Options = preset.Options;
            OnPropertyChanged(nameof(Options));
            _isPresetBeingApplied = false;
            UpdatePreviewAsync().AsTask();
        }

        private async Task SavePresetAsync()
        {
            var nameTextBox = new TextBox { PlaceholderText = "Preset Name" };
            var dialog = new ContentDialog { Title = "Save Preset", Content = nameTextBox, PrimaryButtonText = "Save", CloseButtonText = "Cancel" };
            _windowService.InitializeWithWindow(dialog);
            var result = await dialog.ShowAsync();
            if (result == ContentDialogResult.Primary && !string.IsNullOrWhiteSpace(nameTextBox.Text))
            {
                var newPreset = new ConversionPreset { Name = nameTextBox.Text, Options = this.Options };
                await PresetService.AddPresetAsync(newPreset);
                await LoadPresetsAsync();
                SelectedPreset = Presets.FirstOrDefault(p => p.Name == newPreset.Name);
            }
        }

        private async Task DeletePresetAsync()
        {
            if (SelectedPreset != null)
            {
                await PresetService.DeletePresetAsync(SelectedPreset.Name);
                await LoadPresetsAsync();
                SelectedPreset = null;
            }
        }

        private void RotateImage(RotateDirection direction)
        {
            var current = Options.Rotate;
            int currentVal = (int)current;
            int rotationAmount = direction == RotateDirection.Right ? 90 : -90;
            int newRotationDegrees = (currentVal + rotationAmount + 360) % 360;

            Options.Rotate = (RotateMode)newRotationDegrees;
            OnPropertyChanged(nameof(Options));
            UpdatePreviewAsync().AsTask();
        }

        private DispatcherTimer _debounceTimer;

        private void OnOptionChanged()
        {
            if (_isPresetBeingApplied) return;

            if (_debounceTimer == null)
            {
                _debounceTimer = new DispatcherTimer { Interval = TimeSpan.FromMilliseconds(500) };
                _debounceTimer.Tick += async (s, e) =>
                {
                    await UpdatePreviewAsync();
                    _debounceTimer.Stop();
                };
            }
            _debounceTimer.Stop();
            _debounceTimer.Start();
        }

        private async Task UpdatePreviewAsync()
        {
            if (SelectedFile == null || string.IsNullOrEmpty(SelectedOutputFormat)) return;

            try
            {
                using (var stream = _imageConverter.ConvertImageToStream(SelectedFile.Path, $".{SelectedOutputFormat.ToLower()}", Options))
                {
                    var bitmapImage = new BitmapImage();
                    await bitmapImage.SetSourceAsync(stream.AsRandomAccessStream());
                    ConvertedPreviewImage = bitmapImage;
                }
            }
            catch (Exception ex)
            {
                ConvertedPreviewImage = null;
                await _windowService.ShowContentDialogAsync("Preview Error", $"An error occurred while generating the preview: {ex.Message}");
            }
        }

        private bool _isBusy;
        public bool IsBusy
        {
            get => _isBusy;
            set { _isBusy = value; OnPropertyChanged(); }
        }

        private async Task ProcessBatchConversionAsync(StorageFolder sourceFolder)
        {
            var destinationPicker = new FolderPicker { SuggestedStartLocation = PickerLocationId.PicturesLibrary };
            _windowService.InitializeWithWindow(destinationPicker);
            StorageFolder destinationFolder = await destinationPicker.PickSingleFolderAsync();
            if (destinationFolder == null) return;

            IsBusy = true;
            QueueService.ClearQueue();

            await Task.Run(async () => await AddFolderToQueueRecursively(sourceFolder, destinationFolder));

            IsBusy = false;

            if (App.m_window.Content is MainWindow mainWindow)
            {
                mainWindow.NavigateToPage(typeof(QueuePage));
            }
        }

        private async Task AddFolderToQueueRecursively(StorageFolder currentFolder, StorageFolder destinationFolder)
        {
            var items = await currentFolder.GetItemsAsync();
            foreach (var item in items)
            {
                if (item is StorageFolder subFolder)
                {
                    var newDestFolder = destinationFolder;
                    if (Options.KeepFolderStructure)
                    {
                        newDestFolder = await destinationFolder.CreateFolderAsync(subFolder.Name, CreationCollisionOption.OpenIfExists);
                    }
                    await AddFolderToQueueRecursively(subFolder, newDestFolder);
                }
                else if (item is StorageFile file)
                {
                    var validExtensions = new[] { ".webp", ".gif", ".jpg", ".jpeg", ".png" };
                    string inputExtension = Path.GetExtension(file.Name).ToLower();
                    string outputExtension = $".{SelectedOutputFormat.ToLower()}";

                    if (validExtensions.Contains(inputExtension) && inputExtension != outputExtension)
                    {
                        string newFileName = Path.ChangeExtension(file.Name, outputExtension);
                        var queueItem = new QueueItem
                        {
                            SourcePath = file.Path,
                            DestinationPath = Path.Combine(destinationFolder.Path, newFileName),
                            Options = this.Options,
                            Status = QueueStatus.Pending
                        };
                        QueueService.AddToQueue(queueItem);
                    }
                }
            }
        }

        public event PropertyChangedEventHandler PropertyChanged;
        protected void OnPropertyChanged([CallerMemberName] string propertyName = null)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }
    }

    public enum RotateDirection { Left, Right }
}