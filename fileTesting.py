offlineFile = open("offlineFile.txt","a+")
offlineFile.seek(0)
x=offlineFile.readlines()
print(x)