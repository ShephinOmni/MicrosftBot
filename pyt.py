import random
import string

# Define the possible characters (digits and lowercase letters)
characters = string.digits + string.ascii_lowercase

# Generate a random string of 6 characters
random_string = ''.join(random.choice(characters) for _ in range(6))

print(random_string)
