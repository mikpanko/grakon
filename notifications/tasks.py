from celery.task import task

from notifications.models import NotificationRecipient, notify_user

@task
def send_notifications():
    logger = send_notifications.get_logger()
    logger.info("sending")

    recipient_ids = NotificationRecipient.objects.filter(is_read=False, email_sent=False) \
            .distinct().values_list('recipient', flat=True)

    if len(recipient_ids) > 0:
        for recipient_id in recipient_ids:
            notify_user(recipient_id)

    return recipient_ids