# Task 1,2
def printState():
    print("Red Light is " + str(redLight))
    print("Yellow Light is " + str(yellowLight))
    print("Green Light is " + str(greenLight))

redLight = 1
yellowLight = 0
greenLight = 0
printState()


# Task 3
print(3 + 5)
print("3" + "5")


# Task 4
x = 10 # Intger
y = 20.0 # Float
z = 1j # Complex Number
print(type(x), type(y), type(z), sep='\n')

x = int(1) # is 1 int
y = int(2.8) # is 2 int
z = int("3") # is 3 int

print(type(x), type(y), type(z), sep='\n')


# Task 5
day = "Beautiful"
print(day[1]) # e
print(day[0:5]) # My prediction is Beaut


# Task 6
print(day[-3]) # f
print(day[-3:]) # ful
print(day[-5:3]) # I thought "t", but you need to specify the step to be -1
print(day[-5:-3]) # ti


# Task 7
day == "Beautiful"
print("Today is " + day)

print (str(day == "Beautiful") + ": Today is " + day)


# Task 8
operand1 = input("Input a number: ")
print("You entered " + operand1)