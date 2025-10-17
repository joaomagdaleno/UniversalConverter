using Microsoft.UI.Xaml.Data;
using System;

namespace UniversalConverter
{
    public class BooleanToStringConverter : IValueConverter
    {
        public string TrueValue { get; set; }
        public string FalseValue { get; set; }

        public object Convert(object value, Type targetType, object parameter, string language)
        {
            return (value is bool and true) ? TrueValue : FalseValue;
        }

        public object ConvertBack(object value, Type targetType, object parameter, string language)
        {
            throw new NotImplementedException();
        }
    }
}