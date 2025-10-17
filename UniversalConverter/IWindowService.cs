using System.Threading.Tasks;

namespace UniversalConverter
{
    public interface IWindowService
    {
        void InitializeWithWindow(object target);
        Task ShowContentDialogAsync(string title, string content);
    }
}