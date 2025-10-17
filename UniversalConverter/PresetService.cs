using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Threading.Tasks;
using Windows.Storage;

namespace UniversalConverter
{
    public class ConversionPreset
    {
        public string Name { get; set; }
        public ConversionOptions Options { get; set; }
    }

    public static class PresetService
    {
        private static List<ConversionPreset> _presets = new List<ConversionPreset>();
        private const string PresetsFileName = "presets.json";

        public static IReadOnlyList<ConversionPreset> Presets => _presets.AsReadOnly();

        public static async Task LoadPresetsAsync()
        {
            try
            {
                StorageFile presetsFile = await ApplicationData.Current.LocalFolder.GetFileAsync(PresetsFileName);
                string json = await FileIO.ReadTextAsync(presetsFile);
                _presets = JsonSerializer.Deserialize<List<ConversionPreset>>(json) ?? new List<ConversionPreset>();
            }
            catch (FileNotFoundException)
            {
                _presets = new List<ConversionPreset>();
            }
        }

        private static async Task SavePresetsAsync()
        {
            string json = JsonSerializer.Serialize(_presets);
            StorageFile presetsFile = await ApplicationData.Current.LocalFolder.CreateFileAsync(PresetsFileName, CreationCollisionOption.ReplaceExisting);
            await FileIO.WriteTextAsync(presetsFile, json);
        }

        public static async Task AddPresetAsync(ConversionPreset preset)
        {
            _presets.Add(preset);
            await SavePresetsAsync();
        }

        public static async Task DeletePresetAsync(string presetName)
        {
            var preset = _presets.FirstOrDefault(p => p.Name == presetName);
            if (preset != null)
            {
                _presets.Remove(preset);
                await SavePresetsAsync();
            }
        }
    }
}