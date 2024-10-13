from datetime import datetime, tzinfo

import pytz

from library.utils.built_in.static_class import Static


class DateFactory(Static):
    __TZ_SAO_PAULO = pytz.timezone('America/Sao_Paulo')

    @staticmethod
    def new_date() -> datetime:
        return datetime.now(pytz.utc).astimezone(DateFactory.__TZ_SAO_PAULO)
