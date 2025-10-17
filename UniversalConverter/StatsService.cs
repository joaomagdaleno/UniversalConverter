using System;
using System.IO;
using System.Text.Json;
using System.Threading.Tasks;
using Windows.Storage;

namespace UniversalConverter
{
    public static class StatsService
    {
        private class StatisticsData
        {
            public int TotalConversions { get; set; } = 0;
            public DateTime? LastConversionDate { get; set; } = null;
        }

        private static StatisticsData _stats = new StatisticsData();
        private const string StatsFileName = "stats.json";

        public static int TotalConversions => _stats.TotalConversions;
        public static DateTime? LastConversionDate => _stats.LastConversionDate;
        public static event EventHandler StatsChanged;

        public static async Task LoadAsync()
        {
            try
            {
                StorageFile statsFile = await ApplicationData.Current.LocalFolder.GetFileAsync(StatsFileName);
                string json = await FileIO.ReadTextAsync(statsFile);
                _stats = JsonSerializer.Deserialize<StatisticsData>(json) ?? new StatisticsData();
            }
            catch (FileNotFoundException)
            {
                // Arquivo não encontrado, começa com estatísticas padrão
                _stats = new StatisticsData();
            }
            StatsChanged?.Invoke(null, EventArgs.Empty);
        }

        private static async Task SaveAsync()
        {
            string json = JsonSerializer.Serialize(_stats);
            StorageFile statsFile = await ApplicationData.Current.LocalFolder.CreateFileAsync(StatsFileName, CreationCollisionOption.ReplaceExisting);
            await FileIO.WriteTextAsync(statsFile, json);
        }

        public static async Task RecordConversion()
        {
            _stats.TotalConversions++;
            _stats.LastConversionDate = DateTime.Now;
            await SaveAsync();
            StatsChanged?.Invoke(null, EventArgs.Empty);
        }
    }
}