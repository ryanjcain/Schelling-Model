import random
class Person(object):
    """
    Define a class for a person.

    Attributes:
    group (int) -- what group (e.g. ethnic, racial) the person belongs to
    happiness_threshold (float) -- the fraction of neighbors the person would
        like to have come from the same group as them
    home (Home) -- the home object that the person occupies

    Methods:
    is_unhappy() -- decide if the person is unhappy with the group make-up of
        his neighbors
    move() -- move the person from one home to another
    """

    def __init__(self, group, home=None, happiness_threshold=0.2):
        self.group = group
        self.home = None
        self.happiness_threshold = happiness_threshold
        self.move(home)

    def __repr__(self):
        """
        This is like the __str__() magic method, except that it works in things
            like lists as well.
        """
        return str(self.group)

    def is_unhappy(self):
        """
        Calculate if the person is unhappy with the group makeup of his neighbors.

        Returns:
            is_unhappy (bool)
        """

        number_same = 0
        number_diff = 0

        for n in self.home.neighbors_list:
            if n.occupant is not None:
                if n.occupant.group == self.group:
                    number_same += 1
                else:
                    number_diff += 1

        p_unhappy = float(number_same)/(number_diff+number_same)
        return p_unhappy < self.happiness_threshold


    def move(self, new_home):
        """
        Move the person to a new home.

        Expects:
            new_home (Home) -- the new home for the person

        Returns:
            None, but...
                sets the old home's occupant to None
                sets the new_home occupant to the person
                sets the persons home to new_home
        """

        if self.home is not None:
            self.home.occupant = None
        new_home.occupant = self
        self.home = new_home

class Home(object):
    """
    Define a class for a home object.

    Attributes:
    x (int) -- the x-coordinate for the home's address
    y (int) -- the y-coordinate for the home's address
    neighbors (list) -- the home objects that are adjacent to self
    occupant (Person) -- the person that occupies the house.  If no one lives
        in the house, should be set to None.

    Methods:
        none
    """
    def __init__(self, x, y, occupant = None):
        self.x = x
        self.y = y
        self.neighbors_list = []
        self.occupant = occupant

    def __repr__(self):
        res = '(%g,%g): %s' % (self.x, self.y, self.occupant)
        return res

class City(object):
    """
    Define a City class.  This is the over-arching class for running the
    Schelling model.  It defines and populates the grid, defines neighbors,
    updates homes, etc.

    Attributes:
    nx (int) -- the number of columns in the grid
    ny (int) -- the number of rows in the grid
    ngroups (int) -- the number of ethnic/racial groups
    breakdown (list) -- a list containing the ethnic/racial breakdown of the
        city.  breakdown[i] is the fraction of the city represented by group i.
        The total should be less than one.
    homes (dict) -- the keys of the dictionary are (x,y) tuples -> the addresses
        of the homes.  The values of the dictionary are Home() objects.

    Methods:
    find_neighbors() -- assigns neighbors to each home object created.
    populate_homes() -- randomly places people in the homes
    move_unhappy() -- moves all unhappy people to a new home
    plot() -- make one plot of the current state
    make_plots() -- make a series of plots from the initial state to the
        equilibrium state
    """
    def __init__(self, nx=50, ny=50, happiness_threshold=0.3, ngroups=2,
                breakdown=[0.4,0.5]):
        #Local class variables
        self.breakdown = breakdown
        self.people = []
        self.empty_homes = []

        #Create a grid of homes
        self.homes = {}
        for i in range(nx):
            for j in range(ny):
                self.homes[(i,j)] = Home(i,j)

        #Attributes
        self.nx = nx
        self.ny = ny
        self.ngroups = ngroups
        self.happiness_threshold = happiness_threshold

        #Populate the homes
        self.populate_homes(self.breakdown)
        #Create a list of neighbors
        self.find_neighbors()

    def find_neighbors(self):
        """
        Find the homes adjacent to each home.
        Go through the list of home objects (contained in self.homes.values()).
        For each home, calculate the x, y values of the adjacent homes.  If that
        home exists, add it to the neighbors list of the home in question.
        """

        for home in self.homes.values():
            for x in range((home.x-1),(home.x+2)):
                for y in range((home.y-1),(home.y+2)):
                    if (x,y) in self.homes.keys() and (x,y) != (home.x,home.y):
                        neighbor = self.homes[(x,y)]
                        home.neighbors_list.append(neighbor)

    def populate_homes(self, breakdown):
        """
        Make people (Person objects) to occupy the homes.  Some homes should be
        left empty.  The number of people of group i should be
            breakdown[i]*len(self.homes)
        Each person should be assigned to a random home.

        Expects:
            breakdown (list) -- see the description above

        Returns:
            None, but...
                appends empty homes to self.empty_homes
                appends person objects to self.people
                assigns a home to each person (and assigns that
                    same person to that home.occupant variable)
        """

        for home in self.homes.values():
            self.empty_homes.append(home)


        for i in range(self.ngroups):
            npeople = int(self.breakdown[i] * len(self.homes))
            for p in range(npeople):
                home = self.empty_homes.pop(random.randrange(len(self.empty_homes)))
                person = Person(i, home, self.happiness_threshold)
                self.people.append(person)
                home.occupant = person



    def move_unhappy(self):
        """
        Move people who are unhappy.
        Go through the list of people.  If the person is unhappy, choose a random
            empty home to move them into.  Add their home to the list of empty
            homes.

        Coding hint:  you might want to use the following command:
            new_home = self.empty_homes.pop(random.randrange(len(self.empty_homes)))
        but make sure you know how it works

        Expects:
            none

        Returns:
            n_unhappy (int) -- the number of unhappy people moved
        """

        n_unhappy = 0
        for person in self.people:
            if person.is_unhappy():
                n_unhappy += 1
                new_home = self.empty_homes.pop(random.randrange(len(self.empty_homes)))
                self.empty_homes.append(person.home)
                person.move(new_home)
        return n_unhappy

    def plot(self, title='', file_name='schelling.png'):
        """
        Make one plot of the current state of the city.
        """
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        #If you want to run the simulation with more than 7 colors, you should set agent_colors accordingly
        colors = ['b','r','g','c','m','y','k']
        for person in self.people:
            ax.scatter(
                person.home.x+0.5,
                person.home.y+0.5,
                s = 50.,
                color=colors[person.group]
                )
        ax.set_title(title, fontsize=10, fontweight='bold')
        ax.set_xlim([0, self.nx])
        ax.set_ylim([0, self.ny])
        ax.set_xticks([])
        ax.set_yticks([])
        plt.savefig(file_name)

    def make_plots(self):
        """
        Make plots of the current state of the city.  Iterate until there are
        no more changes or we have taken 100 steps.
        """
        import os
        os.system('rm schelling*.png')
        file_name = 'schelling_000.png'
        title = 'Initial Population'
        self.plot(title=title, file_name=file_name)
        n_unhappy = 999
        counter = 0
        while n_unhappy > 0 and counter < 100:
            counter += 1
            print "Photo count:", counter
            n_unhappy = self.move_unhappy()
            file_name = 'schelling_%03g.png'%(counter)
            title = 'Step %03g'%(counter)
            self.plot(title=title, file_name=file_name)

city = City(10, 10, 0.3, 2, [0.45,0.45])
city.make_plots()
