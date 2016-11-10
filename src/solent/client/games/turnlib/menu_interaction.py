from .menu import menu_new

from solent.exceptions import SolentQuitException
from solent.client.constants import *
from solent.client.term.cgrid import cgrid_new

#
# Responsible for displaying a menu, and exposing interaction points with it.
# This acts as a pipeline for keyboard input and display events. Where the
# game is running, it just passes the events through to the game.
#
CPAIR_MENU_BORDER = SOL_CPAIR_BLACK_CYAN
CPAIR_MENU_TEXT = SOL_CPAIR_T_WHITE
CPAIR_TITLE = SOL_CPAIR_T_WHITE

class MenuInteraction(object):
    def __init__(self, title, cgrid):
        '''
        title
            to display on the console
        '''
        self.title = title
        self.cgrid = cgrid
        #
        self.b_active = True
        #
        self.menu = self.__init_menu()
        self.__init_menu()
        #
        self.title_cgrid = None
        self.__init_title()
        #
        self.menu_cgrid = None
        self.__init_menu_grid()
    def __init_menu(self):
        menu = menu_new()
        menu.add('c', 'continue', self.mi_continue_game)
        menu.add('n', 'new', self.mi_new_game)
        menu.add('l', 'load', self.mi_load_game)
        menu.add('s', 'save', self.mi_save_game)
        menu.add('q', 'quit', self.mi_quit)
        return menu
    def __init_title(self):
        # Later on we could use something like pyfiglet for this. Better would
        # be a single distinct font, similar to what Gollop did with rebelstar.
        self.title_cgrid = cgrid_new(
            width=len(self.title),
            height=1)
        self.title_cgrid.put(
            drop=0,
            rest=0,
            s=self.title,
            cpair=CPAIR_TITLE)
    def __init_menu_grid(self):
        lines = self.menu.get_lines()
        longest_line = 0
        for l in lines:
            longest_line = max( [longest_line, len(l)] )
        #
        # prepare the menu border
        self.menu_cgrid = cgrid_new(
            width=longest_line+4,
            height=len(lines)+2)
        horiz = ' '*(longest_line+4)
        menu_border_height = len(lines)+2
        for idx in range(menu_border_height):
            if idx in (0, menu_border_height-1):
                self.menu_cgrid.put(
                    drop=idx,
                    rest=0,
                    s=horiz,
                    cpair=CPAIR_MENU_BORDER)
            else:
                line = lines[idx-1]
                self.menu_cgrid.put(
                    drop=idx,
                    rest=0,
                    s=' ',
                    cpair=CPAIR_MENU_BORDER)
                self.menu_cgrid.put(
                    drop=idx,
                    rest=1,
                    s=' %s%s '%(line, ' '*(longest_line-len(line))),
                    cpair=CPAIR_MENU_TEXT)
                self.menu_cgrid.put(
                    drop=idx,
                    rest=longest_line+3,
                    s=' ',
                    cpair=CPAIR_MENU_BORDER)
    def _redraw_title(self):
        self.cgrid.blit(
            src_cgrid=self.title_cgrid,
            nail=(0, 0))
    def _redraw_menu(self):
        menu_drop = int((self.cgrid.height / 2) - (self.menu_cgrid.height / 2))
        menu_rest = int((self.cgrid.width / 2) - (self.menu_cgrid.width / 2))
        nail = (menu_drop, menu_rest)
        self.cgrid.blit(
            src_cgrid=self.menu_cgrid,
            nail=nail)
    #
    def mi_continue_game(self):
        print('xxx continue game')
        self.b_active = False
    def mi_new_game(self):
        print('xxx new game')
        self.b_active = False
    def mi_load_game(self):
        print('xxx mi_load_game')
    def mi_save_game(self):
        print('xxx mi_save_game')
    def mi_quit(self):
        raise SolentQuitException()
    #
    def active(self):
        return self.b_active
    def set_active(self, b):
        self.b_active = b
    def accept(self, key):
        if not self.menu.has_key(key):
            return
        fn = self.menu.get_callback(key)
        fn()
    def redraw(self, console):
        self._redraw_title()
        self._redraw_menu()
        console.screen_update(
            cgrid=self.cgrid)

def menu_interaction_new(title, width, height):
    cgrid = cgrid_new(
        width=width,
        height=height)
    ob = MenuInteraction(
        title=title,
        cgrid=cgrid)
    return ob
