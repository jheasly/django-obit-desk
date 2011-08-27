import datetime
from models import Death_notice

from obituary_settings import DATABASE_DAYS_BACK

def delete_old_items():
    """
    Remove old Death_notices and related Obituaries.
    """
    days_back = datetime.timedelta(days=DATABASE_DAYS_BACK)
    old_items = Death_notice.objects.filter(death_notice_created__lte= (datetime.datetime.now() - days_back))
    old_items.delete()
