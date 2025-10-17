using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using System.Threading.Tasks;
using WinRT.Interop;

namespace UniversalConverter
{
    public class WindowService : IWindowService
    {
        public void InitializeWithWindow(object target)
        {
            InitializeWithWindow.Initialize(target, App.m_window.GetWindowHandle());
        }

        public async Task ShowContentDialogAsync(string title, string content)
        {
            ContentDialog dialog = new ContentDialog
            {
                Title = title,
                Content = content,
                CloseButtonText = "Ok",
                XamlRoot = (App.m_window.Content as FrameworkElement).XamlRoot
            };
            await dialog.ShowAsync();
        }
    }
}