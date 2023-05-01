import string
import random

filename = "./6mbfile.txt"
filesize = 6 * 1024 * 1024  # 6 MB

with open(filename, 'w') as file:
    while file.tell() < filesize:
        # Generate random string of 10,000 characters
        text = ''.join(random.choice(string.ascii_letters) for i in range(10000))
        file.write(text)

print(f"File '{filename}' created successfully!")