using Microsoft.VisualStudio.TestTools.UnitTesting;
using UniversalConverter;
using SixLabors.ImageSharp.Processing;
using System.Threading.Tasks;
using Windows.Storage;
using System.IO;
using System;

namespace UniversalConverter.Tests
{
    [TestClass]
    public class ConverterViewModelTests
    {
        [TestMethod]
        public void RotateImage_ShouldCycleCorrectly()
        {
            // Arrange
            var viewModel = new ConverterViewModel();

            // Act & Assert
            // Rotate right
            viewModel.RotateRightCommand.Execute(null);
            Assert.AreEqual(RotateMode.Rotate90, viewModel.Options.Rotate);

            viewModel.RotateRightCommand.Execute(null);
            Assert.AreEqual(RotateMode.Rotate180, viewModel.Options.Rotate);

            viewModel.RotateRightCommand.Execute(null);
            Assert.AreEqual(RotateMode.Rotate270, viewModel.Options.Rotate);

            viewModel.RotateRightCommand.Execute(null);
            Assert.AreEqual(RotateMode.None, viewModel.Options.Rotate);

            // Rotate left
            viewModel.RotateLeftCommand.Execute(null);
            Assert.AreEqual(RotateMode.Rotate270, viewModel.Options.Rotate);

            viewModel.RotateLeftCommand.Execute(null);
            Assert.AreEqual(RotateMode.Rotate180, viewModel.Options.Rotate);

            viewModel.RotateLeftCommand.Execute(null);
            Assert.AreEqual(RotateMode.Rotate90, viewModel.Options.Rotate);

            viewModel.RotateLeftCommand.Execute(null);
            Assert.AreEqual(RotateMode.None, viewModel.Options.Rotate);
        }

        [TestMethod]
        public void SelectedPreset_WhenSet_ShouldApplyOptions()
        {
            // Arrange
            var viewModel = new ConverterViewModel();
            var presetOptions = new ConversionOptions
            {
                JpgQuality = 99,
                WebpQuality = 88,
                KeepAspectRatio = false
            };
            var preset = new ConversionPreset { Name = "Test Preset", Options = presetOptions };

            // Act
            viewModel.SelectedPreset = preset;

            // Assert
            Assert.AreEqual(99, viewModel.Options.JpgQuality);
            Assert.AreEqual(88, viewModel.Options.WebpQuality);
            Assert.IsFalse(viewModel.Options.KeepAspectRatio);
        }

        [TestMethod]
        public async Task HandleDroppedFileAsync_WithFile_ShouldUpdateProperties()
        {
            // Arrange
            var viewModel = new ConverterViewModel();
            var tempFile = await CreateTempStorageFile("test.jpg");

            // Act
            await viewModel.HandleDroppedFileAsync(tempFile);

            // Assert
            Assert.IsNotNull(viewModel.SelectedFile);
            Assert.AreEqual(tempFile.Name, viewModel.SelectedFile.Name);
            Assert.IsNotNull(viewModel.OriginalPreviewImage);

            // Clean up
            File.Delete(tempFile.Path);
        }

        [TestMethod]
        public async Task CanConvert_ShouldBeFalseInitially_AndTrueAfterFileSelected()
        {
            // Arrange
            var viewModel = new ConverterViewModel();
            var convertCommand = (RelayCommand)viewModel.ConvertCommand;

            // Assert - Initially false
            Assert.IsFalse(convertCommand.CanExecute(null));

            // Act
            var tempFile = await CreateTempStorageFile("test2.png");
            await viewModel.HandleDroppedFileAsync(tempFile);

            // Assert - True after file is selected
            Assert.IsTrue(convertCommand.CanExecute(null));

            // Clean up
            File.Delete(tempFile.Path);
        }

        private async Task<StorageFile> CreateTempStorageFile(string fileName)
        {
            var tempPath = Path.GetTempPath();
            var filePath = Path.Combine(tempPath, fileName);
            File.WriteAllText(filePath, "dummy content");
            return await StorageFile.GetFileFromPathAsync(filePath);
        }
    }
}