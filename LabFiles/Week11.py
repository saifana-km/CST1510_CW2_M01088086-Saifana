class Student:
    def __init__(self,MISIS,stdName,mark):
        self.__MISIS = MISIS
        self.__stdName = stdName
        self.__mark = mark
    '''def __init__(self):
        self.__MISIS = "M000"
        self.__stdName = "new student"
        self.__mark = 0 '''
    def __str__(self):
        return f'Student Information: {self.__MISIS}, {self.__stdName} and {self.__mark}'
    def result(self):
        if self.__mark > 40:
            print(f"{self.__stdName} has passed.")
std1 = Student("M0101", "Ali", 79)
std2 = Student("M01088086", "Saifana", 100)
#std3 = Student()
print(std1)