using Microsoft.UI.Xaml.Data;
using System;

namespace UniversalConverter
{
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