import datetime
date = '2021-05-21 11:22:03'
datem = datetime. datetime. strptime(date, "%Y-%m-%d %H:%M:%S")
print(int(datem.hour) * 4 + int(datem.minute) // int(15))
