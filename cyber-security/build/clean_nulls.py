with open("cyber-security/CYBER_SECURITY_ESSENTIALS_AND_LINUX_SECURITY_GUIDE.md", "rb") as f:
    data = f.read()

count = data.count(b"\x00")
print(f"Found {count} null bytes in master markdown.")
if count > 0:
    fixed = data.replace(b"\x00", b"\\0")
    with open("cyber-security/CYBER_SECURITY_ESSENTIALS_AND_LINUX_SECURITY_GUIDE.md", "wb") as f:
        f.write(fixed)
    print("Replaced null bytes in CYBER_SECURITY_ESSENTIALS_AND_LINUX_SECURITY_GUIDE.md")

with open("cyber-security/build/guide_processed.md", "rb") as f:
    data2 = f.read()

count2 = data2.count(b"\x00")
print(f"Found {count2} null bytes in guide_processed.md.")
if count2 > 0:
    fixed2 = data2.replace(b"\x00", b"\\0")
    with open("cyber-security/build/guide_processed.md", "wb") as f:
        f.write(fixed2)
    print("Replaced null bytes in guide_processed.md")
