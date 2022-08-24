test_str = "eins"
test_list = ["eins", "zwei"]

print("'eins' länge: {}".format(len(test_str)))
print("'eins' isinstance: {}".format(isinstance(test_str, list)))
print("'['eins', 'zwei']' länge: {}".format(len(test_list)))
print("'['eins', 'zwei']' isinstance: {}".format(isinstance(test_list, list)))

class Test:
    def __str__(self):
        return "test"

class Test2:
    def __str__(self):
        return "test2"

cls1 = Test()
cls2 = Test2()
cls = [cls1, cls2]
str = " ".join([str(elem) for elem in cls])
print("{}".format(str))
