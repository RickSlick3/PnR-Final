# STUDENTS SHOULD NOT EDIT THIS FILE. IT WILL MAKE UPDATING MORE DIFFICULT

from gopigo import *
import time
import logging


class Pigo(object):
    """GoPiGo parent class... students make their own that inherit this"""

    def __init__(self):
        """establishes midpoint, standard stop distance and motor speed then opens menu"""
        self.MIDPOINT = 90
        self.HARD_STOP_DIST = 10
        self.SAFE_STOP_DIST = 30
        self.RIGHT_SPEED = 200
        self.LEFT_SPEED = 200
        self.turn_track = 0
        self.scan = [None] * 180

        if __name__ == "__main__":  # this makes sure the parent handler doesn't take over student's
            print('-----------------------')
            print('------- PARENT --------')
            print('-----------------------')

            self.set_speed(self.LEFT_SPEED, self.RIGHT_SPEED)
            while True:
                self.stop()
                self.menu()

    ####
    ###############################################
    #### FUNCTIONS INTENDED TO BE REPLACED IN CHILD

    def menu(self):
        """gives options to users, calls requested method"""
        menu = {"n": ("Navigate forward", self.nav),
                "d": ("Dance", self.dance),
                "c": ("Calibrate", self.calibrate),
                "o": ("Open House Demo", self.open_house),
                "q": ("Quit", quit)
                }
        for key in sorted(menu.keys()): # Mr. A, did you copy this from StackOverflow? Yes.
            print(key + ":" + menu[key][0])

        ans = raw_input("Your selection: ")
        menu.get(ans, [None, error])[1]()

    def open_house(self):
        """Cute demo used for open house"""
        choice = raw_input("1) Shy;  2) Spin.. ")
        if choice == "1":
            while True:
                if not self.is_clear():
                    self.beShy()
        else:
            while True:
                if not self.is_clear():
                    for x in range(5):
                        self.encR(2)
                        self.encL(2)
                    self.encR(15)

    def beShy(self):
        """animates a shy withdrawal"""
        self.set_speed(80, 80)
        self.encB(5)
        for x in range(3):
            servo(20)
            time.sleep(.1)
            servo(120)
            time.sleep(.1)
        self.encL(2)
        self.encR(2)
        self.encF(5)

    def nav(self):
        """auto-pilots, tries to maintain direction while avoid obstacles"""
        print("Parent nav")

    # DANCING IS FOR THE CHILD CLASS
    def dance(self):
        """runs a series of methods each animating a dance move"""
        print('Parent dance is lame.')

    ##############################################
    ##### FUNCTIONS NOT INTENDED TO BE OVERWRITTEN
    def set_speed(self, left, right):
        """takes left and right speed 0-255"""
        set_left_speed(left)
        set_right_speed(right)
        print('Left speed set to: '+str(left)+' // Right set to: '+str(right))

    def left(self):
        """shell command for GoPiGo left"""
        left()

    def right(self):
        """shell command for GoPiGo right"""
        right()

    def fwd(self):
        """shell command for GoPiGo fwd"""
        fwd()

    def right_rot(self):
        """encoder free turn"""
        right_rot()

    def left_rot(self):
        """encoder-free turn"""
        left_rot()

    def encF(self, enc, m1=1, m2=1):
        """sets encoder, moves forward, sleeps (18 = 1 wheel rot)"""
        print('Moving '+str((enc/18))+' rotation(s) forward')
        enc_tgt(m1, m2, enc)
        fwd()
        time.sleep(1 * (enc / 18)+.4)

    def encR(self, enc, m1=1, m2=1):
        """sets encoder, right_rot, += turn_track, (18 = 1 wheel rot)"""
        print('Moving '+str((enc/18))+' rotation(s) right')
        enc_tgt(m1, m2, enc)
        right_rot()
        self.turn_track += enc
        time.sleep(1 * (enc / 18)+.4)

    def encL(self, enc, m1=1, m2=1):
        """sets encoder, right_rot, -= turn_track, (18 = 1 wheel rot)"""
        print('Moving '+str((enc/18))+' rotation(s) left')
        enc_tgt(m1, m2, enc)
        left_rot()
        self.turn_track -= enc
        time.sleep(1*(enc/18)+.4)

    def encB(self, enc, m1=1, m2=1):
        """sets an encoder, moves back, sleeps, (18 = 1 wheel rot)"""
        print('Moving '+str((enc/18))+ ' rotations(s) backwards')
        enc_tgt(m1, m2, enc)
        bwd()
        time.sleep(1 * (enc / 18)+.4)

    def servo(self, val):
        """moves the head of the robot to the given degree within 60 from midpoint"""
        if val > self.MIDPOINT-60 and val < self.MIDPOINT+60:
            print('Moving servo to ' + str(val) + 'deg')
            servo(val)
            time.sleep(.1)
        else:
            print('range outside of %d - %d' % (self.MIDPOINT-60, self.MIDPOINT+60))

    def dist(self):
        """takes a measurement from the ultrasonic sensor, prints and returns dist in cm"""
        measurement = us_dist(15)
        time.sleep(.01)
        print('I see something ' + str(measurement) + "cm away")
        return measurement

    def flush_scan(self):
        """resets the scan array"""
        self.scan = [None]*180


    def is_clear(self):
        """does a 3-point scan around the midpoint, returns false if a test fails"""
        print("Running the is_clear method.")
        for x in range((self.MIDPOINT - 15), (self.MIDPOINT + 15), 5):
            self.servo(x)
            scan1 = self.dist()
            # double check the distance
            scan2 = self.dist()
            # if I found a different distance the second time....
            if abs(scan1 - scan2) > 2:
                scan3 = self.dist()
                # take another scan and average the three together
                scan1 = (scan1 + scan2 + scan3) / 3
            self.scan[x] = scan1
            print("Degree: " + str(x) + ", distance: " + str(scan1))
            if scan1 < self.SAFE_STOP_DIST:
                print("Doesn't look clear to me")
                return False
        return True

    def choose_path(self):
        """averages distance on either side of midpoint and turns"""
        print('Considering options...')
        if self.is_clear():
            return "fwd"
        else:
            self.wide_scan()
        avgRight = 0
        avgLeft = 0
        for x in range(self.MIDPOINT-60, self.MIDPOINT):
            if self.scan[x]:
                avgRight += self.scan[x]
        avgRight /= 60
        print('The average dist on the right is '+str(avgRight)+'cm')
        logging.info('The average dist on the right is ' + str(avgRight) + 'cm')
        for x in range(self.MIDPOINT, self.MIDPOINT+60):
            if self.scan[x]:
                avgLeft += self.scan[x]
        avgLeft /= 60
        print('The average dist on the left is ' + str(avgLeft) + 'cm')
        logging.info('The average dist on the left is ' + str(avgLeft) + 'cm')
        if avgRight > avgLeft:
            return "right"
        else:
            return "left"

    def stop(self):
        """spams stop command and moves servo to midpoint"""
        print('All stop.')
        for x in range(3):
            stop()
        self.servo(self.MIDPOINT)
        logging.info("STOP COMMAND RECEIVED")

    def calibrate(self):
        """allows user to experiment on finding centered midpoint and even motor speeds"""
        print("Calibrating...")
        self.servo(self.MIDPOINT)
        response = raw_input("Am I looking straight ahead? (y/n): ")
        if response == 'n':
            while True:
                response = raw_input("Turn right, left, or am I done? (r/l/d): ")
                if response == "r":
                    self.MIDPOINT += 1
                    print("Midpoint: " + str(self.MIDPOINT))
                    self.servo(self.MIDPOINT)
                elif response == "l":
                    self.MIDPOINT -= 1
                    print("Midpoint: " + str(self.MIDPOINT))
                    self.servo(self.MIDPOINT)
                else:
                    print("Midpoint now saved to: " + str(self.MIDPOINT))
                    break
        else:
            print('Okay, remember %d as the correct self.MIDPOINT' % self.MIDPOINT)
        response = raw_input("Do you want to check if I'm driving straight? (y/n)")
        if 'y' in response:
            while True:
                self.set_speed(self.LEFT_SPEED, self.RIGHT_SPEED)
                self.encF(18)
                response = raw_input("Reduce left, reduce right or drive? (l/r/d): ")
                if response == 'l':
                    self.LEFT_SPEED -= 10
                elif response == 'r':
                    self.RIGHT_SPEED -= 10
                elif response == 'd':
                    self.encF(18)
                else:
                    break

    def status(self):
        """prints the voltage, motor power, midpoint and stop dist"""
        print("My power is at "+ str(volt()) + " volts")
        print('Left speed set to: '+str(self.LEFT_SPEED)+' // Right set to: '+str(self.RIGHT_SPEED))
        print('My MIDPOINT is set to: '+ str(self.MIDPOINT))
        print('My safe stop distance is ' + str(self.SAFE_STOP_DIST) + 'cm')
        print('My hard stop distance is ' + str(self.HARD_STOP_DIST) + 'cm')

def error():
    pass

def stop_now():
    try:
        from gopigo import *
        stop()
    except Exception as err:
        print(err)
        print("\nCOULDN'T AUTO-STOP!!\n!!!! CUT POWER !!!!!")

########################
#### MAIN APP


try:
    p = Pigo()
except (KeyboardInterrupt, SystemExit):
    stop_now()
except Exception as ee:
    stop_now()
    logging.error(ee.__str__())
