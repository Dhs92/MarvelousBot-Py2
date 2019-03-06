from datetime import datetime

from pytz import timezone

print(datetime.utcnow())
print(datetime.utcnow().replace(tzinfo=timezone('UTC')).astimezone(timezone('America/New_York')))
print(datetime.now(timezone('UTC')).astimezone(timezone('EST')))
