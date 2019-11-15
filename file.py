import sys

if len(sys.argv) != 2:
    print("usage: file.py <filename>", file=sys.stderr)
    sys.exit(1)

print("Binary: Decimal")

try:
    with open(sys.argv[1]) as f:
        for line in f:
            comment_split = line.split('#')  # ignore comments
            num = comment_split[0].strip()  # binary number in the .ls8 file
            try:
                x = int(num, 2)  # pass in num with base 2 to get integer
            except ValueError:
                continue

            print(f"{x:08b}: {x:d}")  # print binary and decimal

except FileNotFoundError:
    print(f"{sys.argv[0]}: {sys.argv[1]} not found")
    sys.exit(2)
