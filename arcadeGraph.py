"""
File: arcadeGraph.py
Original Author: Trey Walker

Designed to be a visual aid to better
understand what is happening with
objects in Python and the arcade library
"""
import arcade
import random
import math
import time

# These are Global constants to use throughout the game
# Screen width and height refer to how many lines in the grid are created

# Some good starting values (formatted [SCREEN_WIDTH, SCREEN_HEIGHT] at PIXELS_PER_GRID) are:
# [12, 10] at 75 (a good, large visual with a small grid)
# [90, 70] at 5 (this can be slow, but makes a completely black background)
SCREEN_WIDTH = 12
SCREEN_HEIGHT = 10

# Pixels per grid refers to the amount of space (in pixels) between each line on the grid
PIXELS_PER_GRID = 75
FONT_SIZE = PIXELS_PER_GRID // 5

WRAP_AROUND_SCREEN = True
MAX_NUMBER_OF_SHIPS = 9
NUMBER_KEYS = [arcade.key.KEY_1,
               arcade.key.KEY_2,
               arcade.key.KEY_3,
               arcade.key.KEY_4,
               arcade.key.KEY_5,
               arcade.key.KEY_6,
               arcade.key.KEY_7,
               arcade.key.KEY_8,
               arcade.key.KEY_9]

CONTROLS_TEXT = """CONTROLS:
A - call the advance function for all objects once

D - swap between detailed mode (draw sprite of a ship to see angles better)
    and non-detailed mode (draw point to simplify visuals)
    [if you don't have a sprite to use, it simply creates a rotated 30x100 box]

W - Set ships to wrap around the screen when they advance (on or off)

T - Turn on and off the timer to automatically advance ships

Space Bar - Reset board: 1 ship at a random position and velocity on screen

Number keys - When multiple ships on screen, chooses the ship to manipulate with
              the left mouse button or arrow keys

Arrow keys - Adjust velocity of main ship (the first one on screen)
            Up and down arrows adjust velocity in the Y direction
            Left and right arrows adjust velocity in the X direction

Left Mouse Button:
        Single click - Change the main ship's velocity based on the cursor's grid position
                        (Goes to bottom left corner of current grid)
        Double click - Reposition the main ship to the cursor's grid position
                        (Goes to bottom left corner of current grid)

Right Mouse Button - Create an new instance of a ship at the cursor's grid position"""


class Point:
    def __init__(self):
        self.x = 0
        self.y = 0

    """
    Actual X and Actual Y return the exact position on the window
    where the point refers to, not the grid position
    """

    def actualX(self):
        return self.x * PIXELS_PER_GRID

    def actualY(self):
        return self.y * PIXELS_PER_GRID


class Velocity:
    def __init__(self):
        self.dx = 0.0
        self.dy = 0.0

    @property
    def angle(self):
        return self._getDegrees()

    def _getDegrees(self):
        """
        Returns the an angle from [0, 360) based on dx and dy
        """
        # Straight left or right
        if self.dy == 0:
            # At rest angle == 0 degrees
            if self.dx >= 0:
                return 0
            else:
                return 180

        # Straight up or down
        elif self.dx == 0:
            if self.dy > 0:
                return 90
            else:
                return 270

        # Diagonal movement: find theta
        degrees = math.degrees(self._getTheta())
        return self._fixedForQuadrant(degrees)

    def _getTheta(self):
        """
        Returns an angle in radians based on current dx and dy
        """
        opposite = abs(self.dy)
        adjacent = abs(self.dx)

        return math.atan(opposite / adjacent)

    def _fixedForQuadrant(self, angle):
        """
        Returns the given angle adjusted to point in the correct quadrant
        based on dx and dy
        """
        if self.dx >= 0:
            # Quadrants I or IV
            if self.dy >= 0:
                return angle
            else:
                return 360 - angle
        else:
            # Quadrants II or III
            if self.dy >= 0:
                return 180 - angle
            else:
                return 180 + angle


class Ship():
    def __init__(self):
        self.center = Point()
        self.velocity = Velocity()

        # Stuff specifically to draw the ship sprite
        imagePath = "../images/playerShip1_orange.png"
        self.functionalPath = True
        try:
            self.texture = arcade.load_texture(imagePath)
        except:
            self.functionalPath = False

        # Initialize values
        self.reset()

    def advance(self):
        self.center.x += self.velocity.dx
        self.center.y += self.velocity.dy

        if WRAP_AROUND_SCREEN:
            self.wrapOffScreen()

    def wrapOffScreen(self):
        # For X:
        # Left side of screen
        if self.center.x < 0:
            self.center.x = SCREEN_WIDTH
        # Right side of screen
        elif self.center.x > SCREEN_WIDTH:
            self.center.x = 0

        # Bottom of screen
        if self.center.y < 0:
            self.center.y = SCREEN_HEIGHT
        # Top of screen
        elif self.center.y > SCREEN_HEIGHT:
            self.center.y = 0

    def draw(self, detailed, alpha=255):
        # Draw a ship sprite
        if detailed:
            self.drawDetailed(alpha=alpha)

        # Draw a circle representing the point
        else:
            color = (255, 0, 0, alpha)
            arcade.draw_circle_filled(self.center.actualX(), self.center.actualY(),
                                      20, color)
        self.drawInformation(detailed, alpha)

    def drawDetailed(self, alpha=255):
        x = self.center.actualX()
        y = self.center.actualY()

        # The ship sprite points up by default
        # We want 0 degrees to be pointing to the right
        angle = self.velocity.angle - 90

        if self.functionalPath:
            width = self.texture.width
            height = self.texture.height
            arcade.draw_texture_rectangle(x, y, width, height,
                                          self.texture, angle, alpha)
        else:
            color = (255, 0, 0, alpha)
            arcade.draw_rectangle_filled(x, y, 30, 100, color, -angle)

    def drawInformation(self, detailed, alpha=255):
        """
        Draws the info of the ship to the screen: center (position), velocity,
        and (if detailed is true) the angle of the velocity
        """
        textColor = arcade.color.WHITE
        info = f"Center: ({self.center.x}, {self.center.y})\n"
        info += f"Velocity: ({self.velocity.dx}, {self.velocity.dy})"
        if detailed:
            info += f"\nAngle: {self.velocity.angle:.3f}"

        # Detailed info requires 3 lines of text, otherwise just 2
        width = FONT_SIZE * 10
        height = FONT_SIZE * (2.5 + (1 * int(detailed)))

        # Find the point about which the text will be centered
        # Points vary slightly between detailed vs not detailed info
        start_x = self.center.actualX() + (PIXELS_PER_GRID // 2 + (FONT_SIZE * int(detailed)))
        if start_x > SCREEN_WIDTH * PIXELS_PER_GRID - width // 2:
            start_x = SCREEN_WIDTH * PIXELS_PER_GRID - width // 2
        elif start_x < width // 2:
            start_x = width // 2

        start_y = self.center.actualY() + (PIXELS_PER_GRID // 2 + (FONT_SIZE * int(detailed)))
        if start_y >= SCREEN_HEIGHT * PIXELS_PER_GRID - height:
            start_y = SCREEN_HEIGHT * PIXELS_PER_GRID - height
        elif start_y <= 0:
            start_y = height

        # Provide a blue text box so it's easier to read
        color = (0, 0, 255, alpha)
        arcade.draw_rectangle_filled(start_x, start_y, width,
                                     height, color)

        # Draw the text
        arcade.draw_text(info, start_x=start_x, start_y=start_y, font_size=FONT_SIZE,
                         color=textColor, width=width, align="center",
                         anchor_x="center", anchor_y="center")

    def reset(self):
        self.center.x = random.randint(2, SCREEN_WIDTH - 2)
        self.center.y = random.randint(2, SCREEN_HEIGHT - 2)
        self.velocity.dx = random.randint(-3, 3)
        self.velocity.dy = random.randint(-3, 3)


class Layout:
    """
    Defines an oversized grid layout to draw on screen.
    There are SCREEN_WIDTH columns and SCREEN_HEIGHT rows,
    each separated by PIXELS_PER_GRID pixels
    """

    def __init__(self):
        self.width = SCREEN_WIDTH * PIXELS_PER_GRID
        self.height = SCREEN_HEIGHT * PIXELS_PER_GRID
        self.color = arcade.color.BLACK
        self.thickLine = 15
        self.thinLine = 5

    def draw(self, alpha=255):
        # Draw thick horizontal bar at y=0 (offset by thickness)
        arcade.draw_rectangle_filled(self.width // 2, self.thickLine // 2,
                                     self.width, self.thickLine,
                                     self.color)
        # Draw thick vertical bar at x=0 (offset by thickness)
        arcade.draw_rectangle_filled(self.thickLine // 2, self.height // 2,
                                     self.thickLine, self.height,
                                     self.color)

        # Draw horizontal bars
        barCount = self.height // PIXELS_PER_GRID
        for height in range(1, barCount):
            arcade.draw_rectangle_filled(self.width // 2, height * PIXELS_PER_GRID,
                                         self.width, self.thinLine,
                                         self.color)
            # Label each bar
            start_x = self.thickLine
            start_y = height * PIXELS_PER_GRID + 5
            arcade.draw_text(str(height), start_x=start_x, start_y=start_y,
                             font_size=FONT_SIZE, color=self.color)

        # Draw vertical bars
        barCount = self.width // PIXELS_PER_GRID
        for width in range(1, barCount):
            arcade.draw_rectangle_filled(width * PIXELS_PER_GRID, self.height // 2,
                                         self.thinLine, self.height,
                                         self.color)
            # Label each bar
            start_x = width * PIXELS_PER_GRID + 5
            start_y = self.thickLine
            arcade.draw_text(str(width), start_x=start_x, start_y=start_y,
                             font_size=FONT_SIZE, color=self.color)

class HelpWindow:
    """
    This class is to display a help window to see controls while running
    """
    def __init__(self):
        self.x = (SCREEN_WIDTH * PIXELS_PER_GRID) // 2
        self.y = (SCREEN_HEIGHT * PIXELS_PER_GRID) // 2

        self.width = int((SCREEN_WIDTH * PIXELS_PER_GRID) * 0.80)
        self.height = int((SCREEN_HEIGHT * PIXELS_PER_GRID) * 0.80)

    def display(self):
        # Draw box
        color = (127, 127, 127, 255)
        arcade.draw_rectangle_filled(self.x, self.y, self.width, self.height, color)

        # Add left padding to text
        start_x = self.x + (FONT_SIZE * 3)
        textColor = arcade.color.BLACK

        # Draw the text
        arcade.draw_text(CONTROLS_TEXT, start_x=start_x, start_y=self.y, font_size=FONT_SIZE,
                         color=textColor, width=self.width, anchor_x="center", anchor_y="center")


class Game(arcade.Window):
    """
    This class handles all the game callbacks and interaction
    This class will then call the appropriate functions of
    each of the above classes.
    """

    def __init__(self, width, height):
        """
        Sets up the initial conditions of the game
        :param width: Screen width
        :param height: Screen height
        """
        super().__init__(width, height)
        arcade.set_background_color(arcade.color.WHITE)

        # Create a grid background
        self.grid = Layout()

        # Create a list of ships
        self.players = []
        # This is the "main" ship which can be adjusted and repositioned
        self.players.append(Ship())

        # Detailed ships defaults to false (start by drawing points, not sprites)
        self.detailed = False

        # The game does not update on a timer by default
        self.constantUpdate = False
        self.advanceTimer = 0

        self.playerToManipulate = 0

        # Time that the left mouse button was last released (in milliseconds)
        self.timeMouseReleased = int(round(time.time() * 1000))

        # g_alpha is a variable to show how opaque to draw objects
        # 0 == transparent and 255 == opaque
        self.g_alpha = 255

        # Help window variables
        self.helpWindow = HelpWindow()
        self.drawHelpWindow = False

        self.held_keys = set()

    def on_draw(self):
        """
        Called automatically by the arcade framework.
        Handles the responsibility of drawing all elements.
        """

        # clear the screen to begin drawing
        arcade.start_render()

        # Draw each object
        # Want these always visible, no alpha given
        self.grid.draw()
        self.writeCurrentStats()

        i = 0
        for thing in self.players:
            thing.draw(self.detailed, alpha=self.g_alpha)
            # Write the number of the player at the position
            self.writeNumber(thing, i + 1, alpha=self.g_alpha)
            i += 1

        if (self.drawHelpWindow):
            self.helpWindow.display()

    # Write the player that is currently being edited
    def writeNumber(self, ship, number, alpha=255):
        color = arcade.color.WHITE
        start_x = ship.center.actualX() - (FONT_SIZE // 3)
        start_y = ship.center.actualY() - (FONT_SIZE // 1.5)
        if self.detailed:
            arcade.draw_circle_filled(ship.center.actualX(), ship.center.actualY(),
                                      FONT_SIZE // 2, arcade.color.BLACK)

        arcade.draw_text(str(number), start_x=start_x, start_y=start_y,
                         font_size=FONT_SIZE, color=color)

    def writeCurrentStats(self):
        text = f"Editing {self.playerToManipulate + 1} of {len(self.players)}"
        lines = 1
        timerStatus = "Off"
        if self.constantUpdate:
            timerStatus = "On"
        wrapStatus = "Off"
        if WRAP_AROUND_SCREEN:
            wrapStatus = "On"
        text += f"\n Timer: {timerStatus}  Wrap: {wrapStatus}"
        lines += 1
        text += f"\n Hold 'H' for help"
        lines += 1

        # Detailed info requires 3 lines of text, otherwise just 2
        width = FONT_SIZE * 12
        height = FONT_SIZE * (lines + 0.5)

        # Find the point about which the text will be centered
        # Points vary slightly between detailed vs not detailed info
        start_x = width // 1.5

        start_y = (SCREEN_HEIGHT * PIXELS_PER_GRID) - (height // 1.5)
        textColor = arcade.color.BLACK

        # Provide a blue text box so it's easier to read
        arcade.draw_rectangle_filled(start_x, start_y, width,
                                     height, arcade.color.GREEN)

        # Draw the text
        arcade.draw_text(text, start_x=start_x, start_y=start_y, font_size=FONT_SIZE,
                         color=textColor, width=width, align="center",
                         anchor_x="center", anchor_y="center")

    def update(self, delta_time):
        """
        Update each object in the game.
        :param delta_time: tells us how much time has actually elapsed
        For this example, the game only updates when the player presses
        the A key
        """
        self.check_keys()

        if self.g_alpha < 255:
            self.g_alpha += 15

        if self.constantUpdate:
            self.advanceTimer -= 1
            if self.advanceTimer <= 0:
                self.g_alpha = 0
                for ship in self.players:
                    ship.advance()
                self.advanceTimer = 30

    def check_keys(self):
        """
        This function checks for keys that are being held down.
        You will need to put your own method calls in here.
        """
        if arcade.key.LEFT in self.held_keys:
            pass

        if arcade.key.RIGHT in self.held_keys:
            pass

        if arcade.key.UP in self.held_keys:
            pass

        if arcade.key.DOWN in self.held_keys:
            pass

        # Machine gun mode...
        # if arcade.key.SPACE in self.held_keys:
        #    pass

    def on_key_press(self, key: int, modifiers: int):
        """
        Checks which key is pressed. Only runs the first frame in which
        it is pressed
        """
        if key == arcade.key.SPACE:
            self.players[0].reset()
            while len(self.players) > 1:
                self.players.remove(self.players[1])

        elif key == arcade.key.A:
            self.g_alpha = 0
            for thing in self.players:
                thing.advance()

        # Change Y Velocity of main ship
        elif key == arcade.key.UP:
            self.players[0].velocity.dy += 1
        elif key == arcade.key.DOWN:
            self.players[0].velocity.dy -= 1

        # Change X Velocity of main ship
        elif key == arcade.key.RIGHT:
            self.players[0].velocity.dx += 1
        elif key == arcade.key.LEFT:
            self.players[0].velocity.dx -= 1

        # Change detail of all ship sprites
        elif key == arcade.key.D:
            self.detailed = not self.detailed

        # Determine if the ships that move off screen
        # should wrap to the opposite side of the screen
        elif key == arcade.key.W:
            global WRAP_AROUND_SCREEN
            WRAP_AROUND_SCREEN = not WRAP_AROUND_SCREEN

            # Wrap anything off screen
            for ship in self.players:
                ship.wrapOffScreen()

        # Determine if ships are updated on a timer
        elif key == arcade.key.T:
            self.constantUpdate = not self.constantUpdate

        #Determine if help window should display
        elif key == arcade.key.H:
            self.drawHelpWindow = True

        # Determine if the player to manipulate needs to change
        i = 0
        for keyName in NUMBER_KEYS:
            if key == keyName and i < len(self.players):
                self.playerToManipulate = i
            i += 1

    def on_key_release(self, key: int, modifiers: int):
        """
        Removes the current key from the set of held keys.
        """
        if key == arcade.key.H:
            self.drawHelpWindow = False

        if key in self.held_keys:
            self.held_keys.remove(key)

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        """
        Checks which mouse button is clicked. Only runs first frame a button
        is clicked
        """
        # Convert position to grid positions
        newX = x // PIXELS_PER_GRID
        newY = y // PIXELS_PER_GRID

        # Create a new ship object with the right mouse button
        if button == arcade.MOUSE_BUTTON_RIGHT:
            self.manageShipList(newX, newY)

        # Move the main ship object to the mouse's position with the left mouse button
        elif button == arcade.MOUSE_BUTTON_LEFT:
            self.manipulateMainShip(newX, newY)

    def manipulateMainShip(self, x, y):
        currentTime = int(round(time.time() * 1000))

        # Move main ship object to mouse's position with double-click
        if currentTime - self.timeMouseReleased <= 100:
            self.players[self.playerToManipulate].center.x = x
            self.players[self.playerToManipulate].center.y = y

        # Change main ship's velocity with single click
        else:
            self.players[self.playerToManipulate].velocity.dx = x - self.players[self.playerToManipulate].center.x
            self.players[self.playerToManipulate].velocity.dy = y - self.players[self.playerToManipulate].center.y

    def manageShipList(self, x, y):
        existingShip = self.shipAtPoint(x, y)
        shipWasThere = False

        # Remove all ships at specified location 
        while existingShip != None and len(self.players) > 1:
            self.players.remove(existingShip)
            existingShip = self.shipAtPoint(x, y)
            shipWasThere = True

        if shipWasThere:
            while self.playerToManipulate >= len(self.players):
                self.playerToManipulate -= 1
        else:
            # Create a ship at the specified location
            if len(self.players) < MAX_NUMBER_OF_SHIPS:
                newShip = Ship()
                newShip.center.x = x
                newShip.center.y = y

                self.players.append(newShip)

    def shipAtPoint(self, x, y):
        for ship in self.players:
            if ship.center.x == x and ship.center.y == y:
                return ship

        # If we get to this line, then no ships were at that position
        return None

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
        """
        Performs an action when the mouse button is clicked. Only runs
        first frame a button is released
        """

        if button == arcade.MOUSE_BUTTON_LEFT:
            self.timeMouseReleased = int(round(time.time() * 1000))


# Creates the game and starts it going
window = Game(SCREEN_WIDTH * PIXELS_PER_GRID, SCREEN_HEIGHT * PIXELS_PER_GRID)
arcade.run()
