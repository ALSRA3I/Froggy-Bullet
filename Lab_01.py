import math

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


# Program 1
number1 = int(input("Enter the first number: "))
number2 = int(input("Enter the second number: "))

print("The sum: " + str(number1 + number2))
print("The product: " + str(number1 * number2))
print("The ratio: " + str(number1 / number2))
print("The modulus: " + str(number1 % number2))
print("The exponentiation: " + str(number1 ** number2))


# Program 2
temp_c = float(input("Enter the temperature in Celsius: "))

print("The temperature in Fahrenheit: " + str((temp_c * 9 / 5) + 32))


# Program 3
r = float(input("Enter the value of radius: "))
area = math.pi * r**2
circum = 2 * math.pi * r

print("The area: " + str(round(area, 2)), "The circumference: " + str(round(circum, 2)))


# Program 4
r_sphere = float(input("Enter the sphere radius: "))
area_sphere = 4 * math.pi * r**2

print("The sphere area: " + str(round(area_sphere, 2)))


# Program 5
height = float(input("Enter the height of the cylinder: "))
r_cylinder = float(input("Enter the radius of the cylinder: "))

area_cylinder = 2 * math.pi * r_cylinder * height + 2 * math.pi * r_cylinder**2

print("The surface area of cylinder: " + str(round(area_cylinder, 2)))


# Program 6
name = input("Enter your first name: ")
surname = input("Enter your surname: ")

print("Your initials are: " + name[0] + "." + surname[0] + ".")