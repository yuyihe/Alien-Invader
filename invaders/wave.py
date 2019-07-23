"""
Subcontroller module for Alien Invaders

This module contains the subcontroller to manage a single level or wave in the Alien
Invaders game.  Instances of Wave represent a single wave.  Whenever you move to a
new level, you are expected to make a new instance of the class.

The subcontroller Wave manages the ship, the aliens and any laser bolts on screen.
These are model objects.  Their classes are defined in models.py.

Most of your work on this assignment will be in either this module or models.py.
Whether a helper method belongs in this module or models.py is often a complicated
issue.  If you do not know, ask on Piazza and we will answer.

Kathy JaYoung Byun(jb2297), Yuyi He(yh383)
12/4/2018
"""
from game2d import *
from consts import *
from models import *
import random

# PRIMARY RULE: Wave can only access attributes in models.py via getters/setters
# Wave is NOT allowed to access anything in app.py (Subcontrollers are not permitted
# to access anything in their parent. To see why, take CS 3152)


class Wave(object):
    """
    This class controls a single level or wave of Alien Invaders.

    This subcontroller has a reference to the ship, aliens, and any laser bolts on screen.
    It animates the laser bolts, removing any aliens as necessary. It also marches the
    aliens back and forth across the screen until they are all destroyed or they reach
    the defense line (at which point the player loses). When the wave is complete, you
    should create a NEW instance of Wave (in Invaders) if you want to make a new wave of
    aliens.

    If you want to pause the game, tell this controller to draw, but do not update.  See
    subcontrollers.py from Lecture 24 for an example.  This class will be similar to
    than one in how it interacts with the main class Invaders.

    #UPDATE ME LATER
    INSTANCE ATTRIBUTES:
        _ship:   the player ship to control [Ship]
        _aliens: the 2d list of aliens in the wave [rectangular 2d list of Alien or None]
        _bolts:  the laser bolts currently on screen [list of Bolt, possibly empty]
        _dline:  the defensive line being protected [GPath]
        _lives:  the number of lives left  [int >= 0]
        _time:   The amount of time since the last Alien "step" [number >= 0]

    As you can see, all of these attributes are hidden.  You may find that you want to
    access an attribute in class Invaders. It is okay if you do, but you MAY NOT ACCESS
    THE ATTRIBUTES DIRECTLY. You must use a getter and/or setter for any attribute that
    you need to access in Invaders.  Only add the getters and setters that you need for
    Invaders. You can keep everything else hidden.

    You may change any of the attributes above as you see fit. For example, may want to
    keep track of the score.  You also might want some label objects to display the score
    and number of lives. If you make changes, please list the changes with the invariants.

    LIST MORE ATTRIBUTES (AND THEIR INVARIANTS) HERE IF NECESSARY

    _alienDirection: The direction where the wave of aliens moves.
    [either 'left' or 'right']
    _stepRandom: int, the steps that the aliens take before they fire
    _steps: int, how many steps the aliens have taken since the last time they fired
     a bolt
    _generate: boolean, whether or not we should call _randomFire
    _score: int, the score that the player gets in this game
    _state: the current state the game should be in
    _fail: boolean, True if the ship has no more life or any alien dips
    below the defense line, False otherwise
    _allkilled: boolean, True if all aliens are killed
    _popSound: the sound when the ship fires a bolt
    _alienBlastSound: the sound when a alien is destroyed
    _shipBlastSound: the sound when teh ship is destroyed
    """
    # GETTERS AND SETTERS (ONLY ADD IF YOU NEED THEM)
    def getScore(self):
        """
        Return the score that the player gets in this game

        This getter method allow the access to the attribute score
        """
        return self._score

    def getState(self):
        """
        Returns the current state of the game.

        This getter method allow the access to the attribute state
        """
        return self._state

    def setState(self,state):
        """
        Assigns new state of the game

        This setter method is to protect the attribute and allow limited access
        to the attribute state

        Parameter state: The current state of the game
        Precondition: States are one of STATE_PAUSED, STATE_ACTIVE,
        STATE_NEWWAVE, STATE_COMPLETE, STATE_INACTIVE or STATE_CONTINUE
        """
        self._state = state

    def getFail(self):
        """
        Returns the current value of the attribute _fail.

        This getter method allow the access to the attribute _fail
        """
        return self._fail

    def getAllKilled(self):
        """
        Returns the current value of the attribute _allkilled.

        This getter method allow the access to the attribute _allkilled
        """
        return self._allkilled

    def getLife(self):
        """
        Returns the current value of the hidden attribute _lives.

        This getter method allow the access to the hidden attribute _lives
        """
        return self._lives

    # INITIALIZER (standard form) TO CREATE SHIP AND ALIENS
    def __init__(self,speed,live,score):
        """
        Initializes the wave

        Parameter speed: The speed the aliens are marching in the current game
        Precondition: speed is a float greater than 0
        """
        self._aliens = self._createAliens()
        self._ship = Ship(GAME_WIDTH/2,SHIP_BOTTOM,SHIP_WIDTH,SHIP_HEIGHT,
        'ship.png')
        self._dline = GPath(points=[0,DEFENSE_LINE,GAME_WIDTH,DEFENSE_LINE],
        linewidth=LINEWIDTH,linecolor='black')
        self._time = 0
        self._alienDirection = 'right'
        self._bolts=[]
        self._steps = 0
        self._generate = True
        self._lives = live
        self._score = score
        self._state = STATE_ACTIVE
        self._fail= False
        self._allkilled = False
        self._speed = speed
        self._popSound = Sound('pop1.wav')
        self._alienBlastSound = Sound('blast1.wav')
        self._shipBlastSound = Sound('blast2.wav')

    # UPDATE METHOD TO MOVE THE SHIP, ALIENS, AND LASER BOLTS
    def update(self,direction,dt,game):
        """
        Method to update ship, bolt, alien

        Parameter direction: direction of ship
        Precondition: direction is either left or right

        Parameter dt: The time in seconds since last update
        Precondition: dt is a number (int or float)

        Parameter game: the Invader object we are working with
        Precondition: game is an object of Invaders
        """
        if self._generate:
            self._randomFire()
            self._generate = False
        self._moveShip(direction)
        self._alienTime(dt)
        self._createBolt(game)
        self._moveBolts()
        self._alienCollison()
        self._shipCollison()
        self._alienBelowDefense()
        self._alienGone()

    # DRAW METHOD TO DRAW THE SHIP, ALIENS, DEFENSIVE LINE AND BOLTS
    def draw(self,view):
        """
        Draws the game objects to the view.

        Every single thing you want to draw in this game is a GObject.  To draw a GObject
        g, simply use the method g.draw(self.view).  It is that easy!

        Many of the GObjects (such as the ships, aliens, and bolts) are attributes in
        Wave. In order to draw them, you either need to add getters for these attributes
        or you need to add a draw method to class Wave.  We suggest the latter.  See
        the example subcontroller.py from class.
        """
        # IMPLEMENT ME
        for i in self._aliens:
            if i is not None:
                for j in i:
                    if j is not None:
                        j.draw(view)
        if self._ship is not None:
            self._ship.draw(view)
        self._dline.draw(view)
        for x in self._bolts:
            x.draw(view)

    def _createAliens(self):
        """
        Return a 2D list of aliens

        Assign the x, y position and source of each aliens, creates 2D list of
        aliens
        """
        li=[]
        for k in range(ALIENS_IN_ROW):
            list = []
            for i in range(ALIEN_ROWS):
                x=0
                y=0
                x=(k+1)*ALIEN_H_SEP+ALIEN_WIDTH*(k+1/2)
                y=GAME_HEIGHT-(ALIEN_CEILING+(ALIEN_ROWS-0.5-i)*ALIEN_HEIGHT+
                (ALIEN_ROWS-1-i)*ALIEN_V_SEP)
                if i%6==0 or i%6==1:
                    source = 'alien1.png'
                elif i%6==2 or i%6==3:
                    source = 'alien2.png'
                elif i%6==4 or i%6==5:
                    source = 'alien3.png'
                a=Alien(x,y,ALIEN_WIDTH,ALIEN_HEIGHT,source)
                list.append(a)
            li.append(list)
        return li

    def _randomFire(self):
        """
        Pick a random number of steps between 0 and BOLT_RATE to make aliens
        fire randomly.

        Number of steps are numbers from 0 to BOLT_RATE(inclusive)
        """
        self._stepRandom = random.randint(1,BOLT_RATE)

    def _moveShip(self,direction):
        """
        Move the ship to either leeft or right by changing x and y coordinate
        of the ship

        Parameter direction: direction where ship is moving
        Precondition: direction is either left or right
        """
        if direction == left:
            self._ship.x=max(self._ship.x-SHIP_MOVEMENT,SHIP_WIDTH/2)
        elif direction == right:
            self._ship.x=min(self._ship.x+SHIP_MOVEMENT,GAME_WIDTH-SHIP_WIDTH/2)

    def _createBolt(self,game):
        """
        Create a bolt by specifying its x and y coordinate, width, height,
        fillcolor, linecolor and velocity

        Parameter game: the Invader object we are working with
        Precondition: game is an object of Invaders
        """
        if self._fireBolts(game):
            if self._playerNoBolt():
                x = self._ship.x
                y = self._ship.y+1/2*SHIP_HEIGHT
                a = Bolt(x=x,y=y,width=BOLT_WIDTH,height=BOLT_HEIGHT,
                fillcolor='black',linecolor='black',velocity=BOLT_SPEED)
                self._popSound.play()
                self._bolts.append(a)

    def _playerNoBolt(self):
        """
        Return True if there's no player's bolt on the screen, False otherwise

        Method to make sure that only one bolt on the screen belongs to the
        player
        """
        state = True
        for x in self._bolts:
            if x.isPlayerBolt():
                state = False
        return state

    def _fireBolts(self,game):
        """
        Return True if up key was pressed, False otherwise

        Method to determine whether or not the player has decided to fire a bolt

        Parameter game: the Invader object we are working with
        Precondition: game is an object of Invaders
        """
        return game.input.is_key_down("up")

    def _moveBolts(self):
        """
        Method to move all the bolts on the screen.
        If a bolt goes off screen, delete it from the _bolts list
        """
        for b in self._bolts:
            if b.y > GAME_HEIGHT or b.y+BOLT_HEIGHT < 0:
                self._bolts.remove(b)
            else:
                b.y = b.y+b.getVelocity()

    def _alienTime(self,dt):
        """
        Method to march the aliends across the screen.
        It determines when and which direction the aliens should be moving

        Parameter dt: The time in seconds since last update
        Precondition: dt is a number (int or float)
        """
        self._time = self._time+dt
        if self._time > self._speed:
            self._time = 0
            if self._alienDirection == 'right':
                alien = self._bottomRightAlien()
                if alien.x+1/2*ALIEN_WIDTH > GAME_WIDTH-ALIEN_H_SEP:
                    self._alienDirection = 'left'
                    self._shiftAlienDown()
                else:
                    self._shiftAlienRight()
            elif self._alienDirection == 'left':
                alien = self._bottomLeftAlien()
                if alien.x-1/2*ALIEN_WIDTH < ALIEN_H_SEP:
                    self._alienDirection = 'right'
                    self._shiftAlienDown()
                else:
                    self._shiftAlienLeft()

    def _bottomLeftAlien(self):
        """
        Return the bottom left alien in the 2D _aliens list
        """
        for i in self._aliens:
            if i is not None:
                for alien in i:
                    if alien is not None:
                        return alien

    def _bottomRightAlien(self):
        """
        Return the bottom right alien in the 2D _aliens list
        """
        for i in reversed(self._aliens):
            if i is not None:
                for alien in i:
                    if alien is not None:
                        return alien

    def _shiftAlienRight(self):
        """
        Move the aliens to the right by increment ALIEN_H_WALK
        """
        self._steps = self._steps+1
        self._alienFire()
        for i in self._aliens:
            if i is not None:
                for j in i:
                    if j is not None:
                        j.x = j.x+ ALIEN_H_WALK

    def _shiftAlienLeft(self):
        """
        Move the aliens to the left by decrement ALIEN_H_WALK
        """
        self._steps = self._steps+1
        self._alienFire()
        for i in self._aliens:
            if i is not None:
                for j in i:
                    if j is not None:
                        j.x = j.x- ALIEN_H_WALK

    def _shiftAlienDown(self):
        """
        Move the aliens down by decrement ALIEN_V_WALK
        """
        self._steps = self._steps+1
        self._alienFire()
        for i in self._aliens:
            if i is not None:
                for j in i:
                    if j is not None:
                        j.y = j.y- ALIEN_V_WALK

    def _alienFire(self):
        """
        Method to determine when to fire bolts from alien
        Reset attribute steps to 0 everytime an alien fires
        """
        if self._steps==self._stepRandom:
            self._steps = 0
            self._createAlienBolt()

    def _createAlienBolt(self):
        """
        Method to create a bolt fired by an alien and append it to the _bolts
        list Change the _generate attribute to True so now it can randomly
        generate the next bolt
        """
        a = self._whichAlien()
        x = a.x
        y = a.y-1/2*ALIEN_HEIGHT
        b= Bolt(x=x,y=y,width=BOLT_WIDTH,height=BOLT_HEIGHT,fillcolor='black',
        linecolor='black',velocity=-BOLT_SPEED)
        self._bolts.append(b)
        self._generate = True

    def _whichAlien(self):
        """
        Method to randomly pick an alien to fire

        Return the alien that's at the bottom of the column that we randomly
        picked
        Add check function so when everything's none, game's over
        """
        empty = True
        while empty:
            c = random.randint(1,ALIENS_IN_ROW)-1
            if self._aliens[c] is not None:
                for x in range(ALIEN_ROWS):
                    if self._aliens[c][x] is not None:
                        empty = False
                        return self._aliens[c][x]

    def _alienCollison(self):
        """
        Method to deal with alien-bolt collisions

        If an alien collides with a bolt taht's fired from the ship, change the
        position of that alien to None and remove
        the bolt after the collision
        """
        for bolt in self._bolts:
            for i in range(len(self._aliens)):
                if self._aliens[i] is not None:
                    for j in range(len(self._aliens[i])):
                        if self._aliens[i][j] is not None:
                            if self._aliens[i][j].collides(bolt):
                                self._bolts.remove(bolt)
                                self._alienBlastSound.play()
                                self._aliens[i][j] = None
                                self._score = self._score+self.score_determine(j)

    def score_determine(self,j):
        """
        Return the number of points the player gets for destorying this alien

        Method to determine how many points this line of aliens are worth

        The first two lines of aliens are worth 10 points, the thrid and fourth
        line of aliens are worth 20......Every two lines the number of points
        awarded increases by 10 points

        Parameter j: the line that this alien is in
        Precondition: j is an int >= 0
        """
        division = j//2
        score = division*10+10
        return score

    def _shipCollison(self):
        """
        Method to deal with ship-bolt collisions

        If the ship collides with a bolt that's fired from an alien, but the
        ship has more than 1 live, decrease the number of lives the ship has and
        change the state to paused, otherwise change the attribute _ship to None
        and set attribute _fail to True
        """
        for bolt in self._bolts:
            if self._ship is not None:
                if self._ship.collides(bolt):
                    self._bolts.remove(bolt)
                    self._shipBlastSound.play()
                    if self._lives > 1:
                        self._lives = self._lives-1
                        self._state = STATE_PAUSED

                    else:
                        self._ship = None
                        self._fail = True

    def _alienBelowDefense(self):
        """
        Method to determine whether or not the aliens are under the defense line

        If alien goes below defense line, set attribute _fail to True and player
        loses the game
        """
        for i in self._aliens:
            if i is not None:
                for j in i:
                    if j is not None:
                        if j.y-1/2*ALIEN_HEIGHT < DEFENSE_LINE:
                            self._fail = True

    def _alienGone(self):
        """
        Method to determine whether or not all the aliens are killed

        If all aliens are killed, set attribute _allkilled to True and player
        wins the game
        """
        a = True
        for i in self._aliens:
            if i is not None:
                for j in i:
                    if j is not None:
                        a = False
        self._allkilled = a
    # HELPER METHODS FOR COLLISION DETECTION
