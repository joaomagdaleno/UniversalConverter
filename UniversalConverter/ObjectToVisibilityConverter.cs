using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Data;
using System;

namespace UniversalConverter
{
    public class ObjectToVisibilityConverter : IValueConverter
    {
        public object Convert(object value, Type targetType, object parameter, string language)
        {
            if (parameter == null)
            {
                return (value != null) ? Visibility.Visible : Visibility.Collapsed;
            }
            else
            {
                return value != null && value.ToString().Equals(parameter.ToString(), StringComparison.OrdinalIgnoreCase)
                    ? Visibility.Visible
                    : Visibility.Collapsed;
            }
        }

        public object ConvertBack(object value, Type targetType, object parameter, string language)
        {
            throw new NotImplementedException();
        }
    }
}