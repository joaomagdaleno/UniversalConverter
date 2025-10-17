using System.ComponentModel;
using System.Runtime.CompilerServices;

namespace UniversalConverter
{
    public class DashboardViewModel : INotifyPropertyChanged
    {
        public int TotalConversions => StatsService.TotalConversions;
        public string LastConversionDate => StatsService.LastConversionDate.HasValue
            ? StatsService.LastConversionDate.Value.ToString("g")
            : "N/A";

        public DashboardViewModel()
        {
            StatsService.StatsChanged += (s, e) =>
            {
                OnPropertyChanged(nameof(TotalConversions));
                OnPropertyChanged(nameof(LastConversionDate));
            };
        }

        public event PropertyChangedEventHandler PropertyChanged;
        protected void OnPropertyChanged([CallerMemberName] string propertyName = null)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }
    }
}