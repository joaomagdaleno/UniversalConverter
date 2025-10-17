using Microsoft.VisualStudio.TestTools.UnitTesting;
using UniversalConverter;
using SixLabors.ImageSharp.Processing;

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
    }
}