from datetime import datetime, timedelta
from logging import getLogger

from django.apps import apps
from django.db import models
from django.utils.translation import ugettext_lazy as _


logger = getLogger(__file__)

EVENT_TYPES = apps.get_app_config('eventlog').event_type_choices


class EventLogManager(models.Manager):
    def purge(self, days=30):
        """
        Delete all events older than <days> days.
        """
        return self.filter(
            timestamp__gt=datetime.now() - timedelta(days=days)
        ).delete()


class Event(models.Model):
    """
    Event log model.
    """
    type = models.PositiveSmallIntegerField(_('Event Type'), choices=EVENT_TYPES)
    group = models.UUIDField(_('Event Group'))
    timestamp = models.DateTimeField(_('Timestamp'), auto_now_add=True)
    message = models.CharField(_('Message'), max_length=500)
    initiator = models.CharField(_('Initiator'), max_length=500, blank=True, null=True)

    objects = EventLogManager()

    class Meta:
        ordering = ('-timestamp',)
        verbose_name = _('Event Log')
        verbose_name_plural = _('Event Logs')

    def __str__(self):
        return '{group} - {type} - {message}...'.format(
            group=self.group_label(),
            type=self.get_type_display(),
            message=self.message[:40])

    def group_label(self):
        return self.group.hex[-5:]