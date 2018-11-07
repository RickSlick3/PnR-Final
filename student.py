import pigo
import time  # import just in case students need
import random

# setup logs
import logging
LOG_LEVEL = logging.INFO
LOG_FILE = "/home/pi/PnR-Final/log_robot.log"  # don't forget to make this file!
LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"
logging.basicConfig(filename=LOG_FILE, format=LOG_FORMAT, level=LOG_LEVEL)


class Piggy(pigo.Pigo):
    """Student project, inherits teacher Pigo class which wraps all RPi specific functions"""

    def __init__(self):
        """The robot's constructor: sets variables and runs menu loop"""
        print("I have been instantiated!")
        # Our servo turns the sensor. What angle of the servo( ) method sets it straight?
        self.MIDPOINT = 74
        # YOU DECIDE: How close can an object get (cm) before we have to stop?
        self.SAFE_STOP_DIST = 30
        self.HARD_STOP_DIST = 15
        # YOU DECIDE: What left motor power helps straighten your fwd()?
        self.LEFT_SPEED = 137
        # YOU DECIDE: What left motor power helps straighten your fwd()?
        self.RIGHT_SPEED = 137
        # This one isn't capitalized because it changes during runtime, the others don't
        self.turn_track = 0
        # Our scan list! The index will be the degree and it will store distance
        self.scan = [None] * 180
        self.set_speed(self.LEFT_SPEED, self.RIGHT_SPEED)
        # let's use an event-driven model, make a handler of sorts to listen for "events"
        if __name__ == "__main__":
            while True:
                self.stop()
                self.menu()

    def menu(self):
        """Displays menu dictionary, takes key-input and calls method"""
        ## This is a DICTIONARY, it's a list with custom index values
        # You may change the menu if you'd like to add an experimental method
        menu = {"n": ("Navigate forward", self.nav),
                "d": ("Dance", self.dance),
                "o": ("Obstacle count", self.obstacle_count),
                "c": ("Calibrate", self.calibrate),
                "s": ("Check status", self.status),
                "t": ("Test", self.skill_test),
                "h": ("Open House", self.open_house),
                "q": ("Quit", quit_now)
                }
        # loop and print the menu...
        for key in sorted(menu.keys()):
            print(key + ":" + menu[key][0])
        # store the user's answer
        ans = raw_input("Your selection: ")
        # activate the item selected
        menu.get(ans, [None, error])[1]()

    def skill_test(self):
        """Demonstrates two nav skills"""
        choice = raw_input("Left/Right or Turn Until Clear?")

        if "l" in choice:
            self.wide_scan(count=3) # scan the area
            # picks left or right
            # create two variables, left_total and right_total
            left_total = 0
            right_total = 0
            # loop from self.MIDPOINT - 60 to self.MIDPOINT
            for angle in range(self.MIDPOINT - 60, self.MIDPOINT):
                if self.scan[angle]:
                    # add up the numbers to right_total
                    right_total += self.scan[angle]
            # loop from self.MIDPOINT to self.MIDPOINT + 60
            for angle in range(self.MIDPOINT, self.MIDPOINT + 60):
                if self.scan[angle]:
                    # add up the numbers to left_total
                    left_total += self.scan[angle]
            # if right is bigger:
            if right_total > left_total:
                # turn right
                self.encR(4)
            # if left is bigger:
            if left_total > right_total:
                # turn left
                self.encL(4)
        else:
            # turns until clear
            while not self.is_clear():
                self.encR(4)

    def open_house(self):
        """reacts to dist measurement in a cute way"""
        while True:
            if self.dist() < 10:
                for x in range(5):
                    self.servo(69)
                    self.servo(79)
                self.servo(self.MIDPOINT)
                self.encB(5)

            elif self.dist() < 20:
                self.servo(24)
                self.servo(124)
                self.servo(24)
                self.servo(124)
                self.servo(self.MIDPOINT)
                self.encB(5)

            elif self.dist() > 20:
                self.encR(28)
                self.encF(5)
            """Should rotate 360 degrees then roll forward again"""
            time.sleep(.1)

    # YOU DECIDE: How does your GoPiggy dance?
    def dance(self):
        """executes a series of methods that add up to a compound dance"""
        if not self.safe_to_dance():
            print("\n----NOT SAFE TO DANCE----\n")
            return False
        print("\n---- LET'S DANCE ----\n")
        ##### WRITE YOUR FIRST PROJECT HERE
        self.fix()
        self.x_up()
        self.back_step()
        self.shaky_shaky()
        self.sprinkler()
        self.surprise()
        """NOTE: encR(28)~~360, encR(6)~~90"""

    def safe_to_dance(self):
        """circles around and checks for any obstacles"""
        # Check For problems
        for x in range(4):
            if not self.is_clear():
                return False
            self.encR(6)  # IS THIS 90 DEGREES???
        return True

    def fix(self):
        """makes the robot face forward again"""
        self.encR(2)

    def x_up(self):
        """supposed to make an X formation"""
        for x in range(4):
            self.encB(9)
            self.encR(2)
            self.encF(9)
            self.encL(2)
            self.encB(9)
            self.encL(2)
            self.encF(9)
            self.encR(2)

    def back_step(self):
        """supposed to roll forward, then back up 3 separate times"""
        for x in range(3):
            self.encF(18)
            self.encB(6)
            self.encB(6)
            self.encB(6)

    def shaky_shaky(self):
        """supposed to turn back and forth semi-rapidly"""
        for x in range(5):
            self.encR(12)
            self.encL(24)
            self.encR(12)

    def sprinkler(self):
        """supposed to make servo move from side to side"""
        for x in range(5):
            for x in range(self.MIDPOINT-50, self.MIDPOINT+50, 5):
                self.servo(x)

    # FROM GARRET
    def surprise(self):
        """creates the coolest move you have ever seen"""
        for x in range(2):
            self.encF(30)
            self.encL(5)
            self.encB(5)
            self.encR(10)
            self.encB(5)
            self.encL(5)
            self.encB(5)
            self.encR(10)
            self.encB(5)
            self.encL(5)
            self.encB(5)
            self.encR(10)
            self.encB(5)
            self.encL(5)
            self.encB(5)
            self.encR(10)
            self.encB(5)

    def obstacle_count(self):
        """scans and estimates the number of obstacles within sight"""
        self.wide_scan()
        found_something = False
        counter = 0
        for ang, distance in enumerate(self.scan):
            if distance and distance < 150 and not found_something:
                found_something = True
                counter += 1
                print("Object # %d found, I think" % counter)
            if distance and distance > 150 and found_something:
                found_something = False
        print("\n----I SEE %d OBJECTS----\n" % counter)

    def safety_check(self):
        """subroutine of the dance method"""
        self.servo(self.MIDPOINT)  # look straight ahead
        for loop in range(4):
            if not self.is_clear():
                print("NOT GOING TO DANCE")
                return False
            print("Check #%d" % (loop + 1))
            self.encR(8)  # figure out 90 deg
        print("Safe to dance!")
        return True

    def nav(self):
        """auto pilots and attempts to maintain original heading"""
        logging.debug("Starting the nav method")
        print("-----------! NAVIGATION ACTIVATED !------------\n")
        print("-------- [ Press CTRL + C to stop me ] --------\n")
        print("-----------! NAVIGATION ACTIVATED !------------\n")
        while True:
            if self.is_clear():
                self.cruise()
            else:
                self.choose_path()

    def cruise(self):
        """ drive straight while path is clear """
        self.fwd()
        # scans while driving
        while True:
            for angle in range(self.MIDPOINT-20, self.MIDPOINT+21, 10):
                self.servo(angle)
                if self.dist() < self.SAFE_STOP_DIST:
                    self.stop()
                    return

        self.stop()

    def is_clear(self):
        """does a 3-point scan around the midpoint, returns false if a test fails"""
        print("Running the is_clear method.")
        for x in range((self.MIDPOINT - 30), (self.MIDPOINT + 30), 4):
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
                self.servo(self.MIDPOINT)
                return False
        self.servo(self.MIDPOINT)
        return True

    def choose_path(self):
        """turns towards the more open space"""
        self.wide_scan(count=5) # scan the area
        left_total = 0
        right_total = 0
        # loop from self.MIDPOINT - 80 to self.MIDPOINT
        for angle in range(self.MIDPOINT - 80, self.MIDPOINT):
            if self.scan[angle]:
                # add up the numbers to right_total
                right_total += self.scan[angle]
        # loop from self.MIDPOINT to self.MIDPOINT + 80
        for angle in range(self.MIDPOINT, self.MIDPOINT + 80):
            if self.scan[angle]:
                # add up the numbers to left_total
                left_total += self.scan[angle]
        # if right is bigger:
        if right_total > left_total:
            # turn right
            self.encR(4)
        # if left is bigger:
        if left_total > right_total:
            # turn left
            self.encL(4)
        return True

####################################################
############### STATIC FUNCTIONS

def error():
    """records general, less specific error"""
    logging.error("ERROR")
    print('ERROR')


def quit_now():
    """shuts down app"""
    raise SystemExit

##################################################################
######## The app starts right here when we instantiate our GoPiggy


try:
    g = Piggy()
except (KeyboardInterrupt, SystemExit):
    pigo.stop_now()
except Exception as ee:
    logging.error(ee.__str__())