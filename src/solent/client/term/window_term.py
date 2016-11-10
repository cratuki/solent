#
# Pygame wrapper. Provides devices for keystroke and rogue display
#

from .term_shape import term_shape_new
from .cgrid import cgrid_new
from .keystream import keystream_new

from solent.client.constants import *
from solent.exceptions import SolentQuitException

import os
import pygame

PROFILE_RED_T = ((255, 0, 0), (0, 0, 0))
PROFILE_GREEN_T = ((0, 255, 0), (0, 0, 0))
PROFILE_YELLOW_T = ((255, 255, 0), (0, 0, 0))
PROFILE_BLUE_T = ((0, 0, 255), (0, 0, 0))
PROFILE_PURPLE_T = ((255, 0, 255), (0, 0, 0))
PROFILE_CYAN_T = ((0, 255, 255), (0, 0, 0))
PROFILE_WHITE_T = ((255, 255, 255), (0, 0, 0))
PROFILE_T_RED = ((0, 0, 0), (255, 0, 0))
PROFILE_T_GREEN = ((0, 0, 0), (0, 255, 0))
PROFILE_T_YELLOW = ((0, 0, 0), (255, 255, 0))
PROFILE_WHITE_BLUE = ((255, 255, 255), (255, 255, 128))
PROFILE_WHITE_PURPLE = ((255, 255, 255), (255, 0, 255))
PROFILE_BLACK_CYAN = ((0, 0, 0), (0, 255, 255))
PROFILE_T_WHITE = ((0, 0, 0), (255, 255, 255))

MAP_CONST_COLOURS_TO_CPAIR = { SOL_CPAIR_RED_T: PROFILE_RED_T
                             , SOL_CPAIR_GREEN_T: PROFILE_GREEN_T
                             , SOL_CPAIR_YELLOW_T: PROFILE_YELLOW_T
                             , SOL_CPAIR_BLUE_T: PROFILE_BLUE_T
                             , SOL_CPAIR_PURPLE_T: PROFILE_PURPLE_T
                             , SOL_CPAIR_CYAN_T: PROFILE_CYAN_T
                             , SOL_CPAIR_WHITE_T: PROFILE_WHITE_T
                             , SOL_CPAIR_T_RED: PROFILE_RED_T
                             , SOL_CPAIR_T_GREEN: PROFILE_T_GREEN
                             , SOL_CPAIR_T_YELLOW: PROFILE_T_YELLOW
                             , SOL_CPAIR_WHITE_BLUE: PROFILE_WHITE_BLUE
                             , SOL_CPAIR_WHITE_PURPLE: PROFILE_WHITE_PURPLE
                             , SOL_CPAIR_BLACK_CYAN: PROFILE_BLACK_CYAN
                             , SOL_CPAIR_T_WHITE: PROFILE_T_WHITE
                             }

def pygame_getc():
    #events = pygame.event.get()
    while True:
        ev = pygame.event.wait()
        #
        if ev.type == pygame.QUIT:
            raise SolentQuitException()
        if not ev.type == pygame.KEYDOWN:
            continue
        #
        return ev.unicode

class GridDisplay(object):
    def __init__(self, internal_cgrid, font):
        self.internal_cgrid = internal_cgrid
        self.font = font
        #
        width = internal_cgrid.width
        height = internal_cgrid.height
        #
        (self.cwidth, self.cheight) = font.size('@')
        #
        dim = (width * self.cwidth, height * self.cheight)
        self.screen = pygame.display.set_mode(dim)
    def update(self, cgrid):
        cur_dim = (self.internal_cgrid.width, self.internal_cgrid.height)
        new_dim = (cgrid.width, cgrid.height)
        if cur_dim != new_dim:
            self.internal_cgrid.set_dimensions(
                width=cgrid.width,
                height=cgrid.height)
        updates = []
        o_spots = self.internal_cgrid.spots
        n_spots = cgrid.spots
        for idx, (o_spot, n_spot) in enumerate(zip(o_spots, n_spots)):
            if not o_spot.compare(n_spot):
                updates.append(idx)
                o_spot.mimic(n_spot)
        for idx in updates:
            spot = self.internal_cgrid.spots[idx]
            (font_fg, font_bg) = MAP_CONST_COLOURS_TO_CPAIR[spot.cpair]
            label = self.font.render(spot.c, 1, font_fg, font_bg)
            #
            drop_pixels = self.cwidth*int(idx%self.internal_cgrid.width)
            rest_pixels = self.cheight*int(idx/self.internal_cgrid.width)
            self.screen.blit(label, (drop_pixels, rest_pixels))
        pygame.display.flip()


# --------------------------------------------------------
#   :interface
# --------------------------------------------------------
DIR_CODE = os.path.realpath(os.path.dirname(__file__))
DIR_FONT = os.sep.join( [DIR_CODE, 'fonts'] )

#PATH_TTF_FONT = os.sep.join( [DIR_FONT, 'Hack-Bold.ttf'] )
#PATH_TTF_FONT = os.sep.join( [DIR_FONT, 'weird_science_nbp.ttf'] )
#PATH_TTF_FONT = os.sep.join( [DIR_FONT, 'terminus-bold.ttf'] )
PATH_TTF_FONT = os.sep.join( [DIR_FONT, 'kongtext.ttf'] )

CONSOLE = None

def window_term_start(game_width, game_height):
    global CONSOLE
    if None != CONSOLE:
        raise Exception('window_term is singleton. (cannot restart)')
    #
    cgrid = cgrid_new(
        width=game_width,
        height=game_height)
    pygame.font.init()
    font = pygame.font.Font(PATH_TTF_FONT, 16)
    #
    keystream = keystream_new(
        fn_getc=pygame_getc)
    grid_display = GridDisplay(
        internal_cgrid=cgrid,
        font=font)
    CONSOLE = term_shape_new(
        keystream=keystream,
        grid_display=grid_display)
    return CONSOLE

def window_term_end():
    CONSOLE = None
    pygame.quit()

