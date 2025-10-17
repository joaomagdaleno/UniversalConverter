using Microsoft.UI.Xaml.Data;
using System;

namespace UniversalConverter
{
    public class StatusToProgressConverter : IValueConverter
    {
        public object Convert(object value, Type targetType, object parameter, string language)
        {
            if (value is QueueStatus status)
            {
                return status switch
                {
                    QueueStatus.Completed => 100,
                    QueueStatus.InProgress => 50,
                    _ => 0,
                };
            }
            return 0;
        }

        public object ConvertBack(object value, Type targetType, object parameter, string language)
        {
            throw new NotImplementedException();
        }
    }
}