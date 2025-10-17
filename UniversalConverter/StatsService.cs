using System;

namespace UniversalConverter
{
    public static class StatsService
    {
        public static int TotalConversions { get; private set; } = 0;
        public static DateTime? LastConversionDate { get; private set; } = null;

        public static void RecordConversion()
        {
            TotalConversions++;
            LastConversionDate = DateTime.Now;
        }
    }
}