liste = [("abc","passthrough")]

if "DT" not in map(lambda x: x[0], liste):
    print("nicht drin")
else:
    print("drin")