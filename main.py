import requests
import hashlib
from pyfingerprint.pyfingerprint import PyFingerprint


## Main program
def main():
    initializeSensor()
    while(True):
        try:
            print("Welcome to the the Registration Authentiction Unit")
            selection = None
            while(selection != 1 or selection != 2):
                print("Please select an option from below")
                print("\t1:Enroll a fingerprint\n\t2:Mark Attendance")
                ##TODO: Ensure admin user before enrolling a fingerprint
                selection = input()
                if(selection != 1 or selection != 2):
                    print("Invalid selection please try again")
            if(selection == 1):
                enrollFingerprint()
            elif(selection == 2):
                markAttendance()
        except Exception as e:
            print('Operation failed!')
            print('Exception message: ' + str(e))
            exit(1)

def initializeSensor():
    ## Tries to initialize the sensor
    state = None
    while(state == None):
        try:
            print("Initializing fingerprint sensor...")
            f = PyFingerprint('/dev/ttyAMA0', 57600, 0xFFFFFFFF, 0x00000000) 
            if ( f.verifyPassword() == False ):
                raise ValueError('The given fingerprint sensor password is wrong!')
            print("Fingerprint sensor successfully initialized")
            state = 1
        except Exception as e:
            print('The fingerprint sensor could not be initialized!')
            print('Exception message: ' + str(e))
def markAttendance():
    ID = input("Please enter ID of student")
    url = 'http://192.168.0.12:5000/api/fingerprint/' + str(ID)
    r = requests.get(url)
    r.raise_for_status()
    response = r.json()
    #print(response)
    print('Waiting for finger...')  
    ## Wait that finger is read
    while ( f.readImage() == False ):
        pass
    ## Converts read image to characteristics and stores it in charbuffer 1
    f.convertImage(0x01)
    print("Input finger")
    scannedFinger = f.downloadCharacteristics(0x01)
    characteristics = str(f.downloadCharacteristics(0x01)).encode('utf-8')
    print("SCANNED FINGER")
    print(scannedFinger)
    print("====================================================")
    for x in response:
        temp = x["fingerprint"].split(", ")
        temp[0] = temp[0].split("[")[1]
        temp[len(temp)-1] = temp[len(temp)-1].split("]")[0]
        results = list(map(int, temp))
        print (results) 
        f.uploadCharacteristics(0x02,results)
        score = f.compareCharacteristics()
        if(score > 0):
            break 
    if (score != 0):
        print("Finger found!")
        print("With an accuracy score: "+ str(score))
        print(results)
    else:
        print("Finger not found")

def enrollFingerprint():
    ## Tries to enroll a new finger
    print('Please enter ID of student...')
    ID = input()
    print('Waiting for finger...')
    #Wait that finger is read
    while(f.readImage() == False):
        pass
    ## Converts read image to characteristics and stored it in charbuffer 1
    f.convertImage(0x01)
    #TODO: Check if fingerprint is already enrolled
    #Checks if finger is already enrolled
    # result = f.searchTemplate()
    # positionNumber = result[0]
    # if (positionNumber >= 0):
    #     print('Template already exists at postition #' + str(positionNumber))
    #     exit(0)
    print('Remove finger...')
    time.sleep(2)
    print('Place same finger...')
    #Wait until that finger is read again
    while(f.readImage() == False):
        pass
    ##Converts read image to characterisitics and stored it in charbuffer 2            
    f.convertImage(0x02)
    ## Compares the charbuffers
    if( f.compareCharacteristics() == 0):
        raise Exception('Fingers do not match')
    ##Creates a template
    f.createTemplate()
    ##Saves template at new position number
    #positionNumber = f.storeTemplate()
    characteristics = str(f.downloadCharacteristics(0x01)).encode('utf-8')
    print(characteristics)
    print('New template position #' + str(positionNumber))
    payload = {'studentID':str(ID),'fingerprint':characteristics}
    r = requests.post('http://192.168.0.12:5000/api/fingerprint',json = payload)
    r.raise_for_status()
    print("Success")
    print(r.text)

if __name__ == '__main__':
    main()
