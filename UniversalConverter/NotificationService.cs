using Microsoft.Toolkit.Uwp.Notifications;

namespace UniversalConverter
{
    public static class NotificationService
    {
        public static void ShowBatchCompleteNotification(int successCount, int failCount)
        {
            new ToastContentBuilder()
                .AddText("Conversão em Lote Concluída")
                .AddText($"{successCount} arquivos convertidos com sucesso, {failCount} falhas.")
                .Show();
        }
    }
}