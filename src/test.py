import psutil

print("{0:17s}{1:} CPUs PHYSICAL".format("psutil:", psutil.cpu_count(logical=False)))
print("{0:17s}{1:} CPUs LOGICAL".format("psutil:", psutil.cpu_count(logical=True)))
