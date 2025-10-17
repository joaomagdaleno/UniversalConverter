using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Data;
using System;

namespace UniversalConverter
{
    public class BooleanToVisibilityConverter : IValueConverter
    {
        public object Convert(object value, Type targetType, object parameter, string language)
        {
            return (value is bool and true) ? Visibility.Visible : Visibility.Collapsed;
        }

        public object ConvertBack(object value, Type targetType, object parameter, string language)
        {
            return (value is Visibility and Visibility.Visible);
        }
    }
}