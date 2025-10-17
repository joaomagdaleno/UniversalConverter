using Microsoft.UI.Xaml.Data;
using System;

namespace UniversalConverter.Converters
{
    public class StatusToProgressConverter : IValueConverter
    {
        public object Convert(object value, Type targetType, object parameter, string language)
        {
            if (value is QueueStatus status)
            {
                return status == QueueStatus.Completed ? 100 : 0;
            }
            return 0;
        }

        public object ConvertBack(object value, Type targetType, object parameter, string language)
        {
            throw new NotImplementedException();
        }
    }

    public class StatusToIndeterminateConverter : IValueConverter
    {
        public object Convert(object value, Type targetType, object parameter, string language)
        {
            return value is QueueStatus status && status == QueueStatus.InProgress;
        }

        public object ConvertBack(object value, Type targetType, object parameter, string language)
        {
            throw new NotImplementedException();
        }
    }
}