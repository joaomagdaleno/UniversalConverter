using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Runtime.CompilerServices;
using System.Windows.Input;
using Microsoft.UI.Dispatching;

namespace UniversalConverter
{
    public class QueueViewModel : INotifyPropertyChanged
    {
        public ObservableCollection<QueueItem> Queue => QueueService.Queue;
        public ICommand StartCommand { get; }
        public ICommand PauseCommand { get; }
        public ICommand ClearCommand { get; }

        public QueueViewModel()
        {
            StartCommand = new RelayCommand(_ => QueueService.StartProcessing());
            PauseCommand = new RelayCommand(_ => QueueService.PauseProcessing());
            ClearCommand = new RelayCommand(_ => QueueService.ClearQueue());
        }

        public void Initialize(DispatcherQueue dispatcher)
        {
            QueueService.Initialize(dispatcher);
        }

        public event PropertyChangedEventHandler PropertyChanged;
        protected void OnPropertyChanged([CallerMemberName] string propertyName = null)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }
    }
}