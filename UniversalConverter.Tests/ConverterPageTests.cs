using Microsoft.VisualStudio.TestTools.UnitTesting;
using UniversalConverter;
using SixLabors.ImageSharp.Processing;

namespace UniversalConverter.Tests
{
    [TestClass]
    public class ConverterPageTests
    {
        [TestMethod]
        public void GetNewRotation_ShouldCycleCorrectly()
        {
            // Arrange
            var page = new ConverterPage();
            var privateObject = new PrivateObject(page);

            // Act & Assert
            // Rotate right
            var result = (RotateMode)privateObject.Invoke("GetNewRotation", RotateMode.Rotate90);
            Assert.AreEqual(RotateMode.Rotate90, result);

            page.GetType().GetField("_currentRotation", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance).SetValue(page, result);
            result = (RotateMode)privateObject.Invoke("GetNewRotation", RotateMode.Rotate90);
            Assert.AreEqual(RotateMode.Rotate180, result);

            page.GetType().GetField("_currentRotation", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance).SetValue(page, result);
            result = (RotateMode)privateObject.Invoke("GetNewRotation", RotateMode.Rotate90);
            Assert.AreEqual(RotateMode.Rotate270, result);

            page.GetType().GetField("_currentRotation", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance).SetValue(page, result);
            result = (RotateMode)privateObject.Invoke("GetNewRotation", RotateMode.Rotate90);
            Assert.AreEqual(RotateMode.None, result);

            // Rotate left
            page.GetType().GetField("_currentRotation", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance).SetValue(page, RotateMode.None);
            result = (RotateMode)privateObject.Invoke("GetNewRotation", RotateMode.Rotate270);
            Assert.AreEqual(RotateMode.Rotate270, result);

            page.GetType().GetField("_currentRotation", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance).SetValue(page, result);
            result = (RotateMode)privateObject.Invoke("GetNewRotation", RotateMode.Rotate270);
            Assert.AreEqual(RotateMode.Rotate180, result);

            page.GetType().GetField("_currentRotation", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance).SetValue(page, result);
            result = (RotateMode)privateObject.Invoke("GetNewRotation", RotateMode.Rotate270);
            Assert.AreEqual(RotateMode.Rotate90, result);

            page.GetType().GetField("_currentRotation", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance).SetValue(page, result);
            result = (RotateMode)privateObject.Invoke("GetNewRotation", RotateMode.Rotate270);
            Assert.AreEqual(RotateMode.None, result);
        }
    }
}