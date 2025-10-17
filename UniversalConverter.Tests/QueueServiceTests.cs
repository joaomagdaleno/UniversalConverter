using Microsoft.VisualStudio.TestTools.UnitTesting;
using System.Linq;
using System.Threading.Tasks;
using UniversalConverter;

namespace UniversalConverter.Tests
{
    [TestClass]
    public class QueueServiceTests
    {
        [TestInitialize]
        public void Initialize()
        {
            QueueService.ClearQueue();
        }

        [TestMethod]
        public async Task QueueService_PauseAndResume_ProcessesOnlyPendingItems()
        {
            // Arrange
            var options = new ConversionOptions();
            QueueService.AddToQueue(new QueueItem { SourcePath = "item1", DestinationPath = "dest1", Options = options, Status = QueueStatus.Completed });
            QueueService.AddToQueue(new QueueItem { SourcePath = "item2", DestinationPath = "dest2", Options = options, Status = QueueStatus.Pending });
            QueueService.AddToQueue(new QueueItem { SourcePath = "item3", DestinationPath = "dest3", Options = options, Status = QueueStatus.Pending });

            // Act
            QueueService.StartProcessing();
            await Task.Delay(100); // Give it a moment to process one item
            QueueService.PauseProcessing();

            // Assert: Check that the first pending item is now in progress or completed
            var item2 = QueueService.Queue.First(i => i.SourcePath == "item2");
            Assert.IsTrue(item2.Status == QueueStatus.InProgress || item2.Status == QueueStatus.Completed, "Item 2 should have started processing.");

            // Act 2
            QueueService.StartProcessing();
            await Task.Delay(200); // Give it time to finish

            // Assert 2
            var item3 = QueueService.Queue.First(i => i.SourcePath == "item3");
            Assert.IsTrue(item3.Status == Queue.Status.Completed, "Item 3 should have completed after resuming.");
            Assert.IsFalse(QueueService.IsRunning, "Queue should not be running after completion.");
        }
    }
}