using System.Collections.ObjectModel;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.UI.Dispatching;

namespace UniversalConverter
{
    public static class QueueService
    {
        private static readonly ImageConverter _converter = new ImageConverter();
        private static CancellationTokenSource _cancellationTokenSource;
        private static DispatcherQueue _dispatcherQueue;

        public static ObservableCollection<QueueItem> Queue { get; } = new ObservableCollection<QueueItem>();
        public static bool IsRunning { get; private set; } = false;

        public static void Initialize(DispatcherQueue dispatcherQueue)
        {
            _dispatcherQueue = dispatcherQueue;
        }

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
            // Create a snapshot of the queue to avoid collection modified exception
            var queueSnapshot = Queue.ToList();
            
            foreach (var item in queueSnapshot)
            {
                if (token.IsCancellationRequested)
                {
                    break;
                }

                item.Status = QueueStatus.InProgress;
                try
                {
                    await Task.Run(() => _converter.ConvertImage(item.SourcePath, item.DestinationPath, item.Options), token);
                    item.Status = QueueStatus.Completed;
                }
                catch (System.OperationCanceledException)
                {
                    item.Status = QueueStatus.Pending;
                }
                catch (System.Exception ex)
                {
                    // Update status on UI thread
                    _dispatcherQueue?.TryEnqueue(() => item.Status = QueueStatus.InProgress);
                    
                    try
                    {
                        await Task.Run(() => _converter.ConvertImage(item.SourcePath, item.DestinationPath, item.Options));
                        
                        // Record the conversion in statistics
                        await StatsService.RecordConversion();
                        
                        // Update status on UI thread
                        _dispatcherQueue?.TryEnqueue(() => item.Status = QueueStatus.Completed);
                    }
                    catch (System.Exception ex)
                    {
                        // Update status on UI thread
                        _dispatcherQueue?.TryEnqueue(() =>
                        {
                            item.Status = QueueStatus.Failed;
                            item.Message = ex.Message;
                        });
                    }
                }
            }
            IsRunning = false;
        }
    }
}