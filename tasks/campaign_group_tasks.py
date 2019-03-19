from __future__ import unicode_literals
from bloom import celery_app


@celery_app.task(bind=True)
def update_campaigns_in_campaign_group(self, group):
    group.update_text_grouping()

    try:
        print('Finished campaign group ' + str(group.client.client_name) + ' ' + str(group.id))
    except AttributeError:
        print('Something happened with this group ' + str(group.id))

