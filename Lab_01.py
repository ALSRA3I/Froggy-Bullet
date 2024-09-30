def printState():
    print("Red Light is " + str(redLight))
    print("Yellow Light is " + str(yellowLight))
    print("Green Light is " + str(greenLight))

redLight = 1
yellowLight = 0
greenLight = 0
printState()

print(3 + 5)
print("3" + "5")


x = 10 # Intger
y = 20.0 # Float
z = 1j # Complex Number

print(type(x), type(y), type(z), sep='\n')

x = int(1) # is 1 int
y = int(2.8) # is 2 int
z = int("3") # is 3 int

print(type(x), type(y), type(z), sep='\n')


day = "Beautiful"
print(day[1])
print(day[0:5]) # My prediction is Beaut