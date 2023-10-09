from datetime import datetime
import re
x = 'Thu, 15 Jun 2023 00: 00: 00 GMT'
date_string = x.replace('GMT','')


print(date_string)
datetime_object = datetime.strptime(
    date_string, '%a, %d %b %Y %H: %M: %S ').strftime("%Y-%m-%d")

print(datetime_object)
