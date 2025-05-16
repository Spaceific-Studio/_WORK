class Student:
    def __init__(self, name, grade, age):
        self.name = name
        self.grade = grade
        self.age = age
    def __repr__(self):
        return repr((self.name, self.grade, self.age))
stud_objects = [Student("Jan", "ing", 15) \
	           ,Student("Ambroz", "mgr", 50) \
	           ,Student("Feri", "judr", 54) \
	           ,Student("Emil", "ing", 13)]
print vars(Student)
print "stud_objects"
print stud_objects
stud_objects.sort(key = lambda c : c.grade, reverse=True)
print "stud_objects sorted"
print stud_objects

a = [5,2,3,4,5,6]
b = ["timber", "beton", "beblo", "dyka","dyla","fuck"]
zipped = zip(a, b)
print zipped
myList = sorted(zipped, key = lambda a: a[0])

print myList
aSorted, bSorted = zip(*myList)
print "aSorted"
print aSorted
print "bSorted"
print bSorted
print stud_objects[0]