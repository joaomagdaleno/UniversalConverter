using System.Collections.ObjectModel;
using System.Threading;
using System.Threading.Tasks;

namespace UniversalConverter
{
    public static class QueueService
    {
        private static readonly ImageConverter _converter = new ImageConverter();
        private static CancellationTokenSource _cancellationTokenSource;

        public static ObservableCollection<QueueItem> Queue { get; } = new ObservableCollection<QueueItem>();
        public static bool IsRunning { get; private set; } = false;

        public static void AddToQueue(QueueItem item)
        {
            Queue.Add(item);
        }

        public static void StartProcessing()
        {
            if (IsRunning) return;

            IsRunning = true;
            _cancellationTokenSource = new CancellationTokenSource();
            Task.Run(() => ProcessQueueAsync(_cancellationTokenSource.Token));
        }

        public static void PauseProcessing()
        {
            if (!IsRunning) return;

            _cancellationTokenSource?.Cancel();
            IsRunning = false;
        }

        public static void ClearQueue()
        {
            PauseProcessing();
            Queue.Clear();
        }

        private static async Task ProcessQueueAsync(CancellationToken token)
        {
            foreach (var item in Queue)
            {
                if (token.IsCancellationRequested)
                {
                    break;
                }

                if (item.Status == QueueStatus.Pending)
                {
                    item.Status = QueueStatus.InProgress;
                    try
                    {
                        await Task.Run(() => _converter.ConvertImage(item.SourcePath, item.DestinationPath, item.Options));
                        item.Status = QueueStatus.Completed;
                    }
                    catch (System.Exception ex)
                    {
                        item.Status = QueueStatus.Failed;
                        item.Message = ex.Message;
                    }
                }
            }
            IsRunning = false;
        }
    }
}