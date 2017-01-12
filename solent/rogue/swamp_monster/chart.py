#
# chart
#
# // license
# Copyright 2016, Free Software Foundation.
#
# This file is part of Solent.
#
# Solent is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# Solent is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# Solent. If not, see <http://www.gnu.org/licenses/>.

from collections import OrderedDict as od

class Chart:
    '''
    Simple mechanism for mapping a spot (tuple of drop and rest) to a sigil_h.
    '''
    def __init__(self, height, width):
        self.height = height
        self.width = width
        #
        self.d = od()
    def rm(self, spot):
        del self.d[spot]
    def put(self, spot, sigil_h):
        if None == sigil_h:
            del self.d[spot]
        else:
            self.d[spot] = sigil_h
    def blit(self, chart):
        '''
        Copy all the non-void references of the supplied chart into our chart.
        '''
        for (spot, sigil_h) in chart.items():
            self.d[spot] = sigil_h
    def items(self):
        'Returns [ (spot, sigil_h) ]'
        return self.d.items()
    def __repr__(self):
        grid = [[]]
        drop = None
        for (spot, sigil_h) in sorted(self.d.items()):
            if drop == None:
                drop = spot[0]
            elif spot[0] != drop:
                grid.append([])
                drop = spot[0]
            grid[-1].append(sigil_h)
        #
        sb = []
        for row in grid:
            sb.append(''.join(row))
        return '\n'.join(sb)

def chart_new(height, width):
    ob = Chart(
        height=height,
        width=width)
    return ob

