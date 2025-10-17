using System.ComponentModel;
using System.Runtime.CompilerServices;

namespace UniversalConverter
{
    public enum QueueStatus
    {
        Pending,
        InProgress,
        Completed,
        Failed
    }

    public class QueueItem : INotifyPropertyChanged
    {
        private QueueStatus _status;
        private string _message;

        public string SourcePath { get; set; }
        public string DestinationPath { get; set; }
        public ConversionOptions Options { get; set; }
        public string FileName => System.IO.Path.GetFileName(SourcePath);

        public QueueStatus Status
        {
            get => _status;
            set
            {
                _status = value;
                OnPropertyChanged();
            }
        }

        public string Message
        {
            get => _message;
            set
            {
                _message = value;
                OnPropertyChanged();
            }
        }

        public event PropertyChangedEventHandler PropertyChanged;

        protected void OnPropertyChanged([CallerMemberName] string propertyName = null)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }
    }
}