#
# Scheduling mechanism that allows for different things to happen at different
# times. Everything in here orients around meeps. If you want to do things
# that involve time and which don't inherently have meeps, then create a
# hidden plane and put some meeps on it. Meeps are easy to work with,
# time_system is oriented around meeps.
#
# The mechanism below is fairly simple, but possible not to read. Each meet
# has an 'overhead'. That is - the energy hit taken by making a turn. Whenever
# a meep has a turn, it is given a fatigue value equal to its overhead. At the
# same time, all the meeps who have not just had a turn get one deducted from
# their fatigue. In this way, fast things get more turns, and slow things get
# fewer turns. (There's a bit more to it than that, the logic is arranged to
# discourage starvation, but I won't go into that here)
#
# There's a significant inefficiency in the way that the priority list works
# at the time of writing. The reason I've gone with this approach is that I
# needed to do insertion to a queue. Python doesn't support insertion to deque
# before python 3.5. And I don't want to spend energy writing a more efficient
# implementation unless there's a need for it.
#

from .meep import meep_new
from .mind import mind_interface

from collections import deque
import time

def sleep(t):
    print('sleep t [%s]'%t)
    time.sleep(t)

class Initiative(object):
    def __init__(self, sleep_per_tick):
        '''
        sleep_per_tick
            If this is zero, then the clock will skip forward to the next turn
            as soon as it can. If it has a value, then it will sleep for that
            value on each tick of the clock. In practice, you want this to be
            zero for turn-based games, and non-zero for arcade style games.

            At some future point we'll need to refactor this so that the
            sleep does not itself happen in this class, but rather it won't
            proceed until a certain amount of time has passed. The passage
            of time should always be at the discretion of the central event
            loop.
        '''
        self.sleep_per_tick = sleep_per_tick
        #
        # List of meeps, maintained in a deliberate order. The ordering of
        # this list is the heart of the time mechanism.
        self.prio = []
        #
        # We store meeps here who are due to have a turn in the current
        # round.
        self.prepped = deque()
        #
        # Meeps who have had a turn in the current round, and who have
        # not yet been added back into prio.
        self.settled = deque()
    def add_meep(self, meep):
        '''
        Find or create the fatigue run that matches the meep's fatigue. If
        there are other meeps already on the rung, the insertion meep gets
        last spot on the rung.
        '''
        b_placed = False
        for idx in range(len(self.prio)):
            if self.prio[idx].fatigue > meep.fatigue:
                self.prio.insert(idx, meep)
                b_placed = True
                break
        if not b_placed:
            self.prio.append(meep)
    def dispatch_next_tick(self):
        '''finds the next tick that it to be dispatched, and then activates
        all the meeps who are to have their turn.
        '''
        if not self.prio and not self.prepped:
            return False
        activity = False
        #
        # Identifies the meeps who have become due for a turn, and prepares
        # for their turn. Sometimes the previous call to dispatch_next_tick
        # will have had left-over tasks that were not completed. That's the
        # reason for this if.
        if 0 == len(self.prepped):
            # Synchronise time so that the first item in the list is at 0
            # fatigue.
            if self.sleep_per_tick:
                sleep(
                    t=self.sleep_per_tick)
            else:
                self._normalise_time_to_next_rung()
            #
            # Find all of the meeps who have zero fatigue. It's going to be
            # their turn. So we move them from our prio list into a team list.
            while self.prio and self.prio[0].fatigue == 0:
                # (The mechanism by which we are doing this at the moment is
                # probably inefficient. See comments at top. We can't use a
                # deque for self.prio because we ability to insert to it
                # elsewhere.)
                meep = self.prio[0]
                del self.prio[0]
                self.prepped.append(meep)
        #
        # Attempt to give turns to each of the prepped meeps
        while self.prepped:
            meep = self.prepped.popleft()
            if meep.has_died:
                # Here, the dead meep falls out of the list simply by neglect:
                # we fail to re-add it.
                continue
            mind = meep.mind
            if None == mind:
                # I can't think of a valid situation where this would happen,
                # but don't want to be concerned with the situation or the
                # consequences here. "nothing to see here, please disperse".
                continue
            if not mind.ready():
                # Here, we deduce that the meep that needs processing cannot
                # proceed with its turn. This effectively calls a break
                # against this function: we can do no more turn processing
                # until we get that input.
                self.prepped.appendleft(meep)
                return activity
            mind.turn(meep)
            activity = True
            meep.fatigue += meep.overhead
            self.settled.append(meep)
        #
        # If we get this far, it means that we've processed all of our
        # prepped queue into our settled queue.
        #
        # Reduce fatigue for the other meeps. i.e. those that have not had
        # a turn in the current round.
        for itm in self.prio:
            itm.fatigue -= 1
        #
        # Now restore our settled meeps to the queue. (For each meep, we
        # locate the relevant fatigue rung, and then place them at the end of
        # that rung. This avoids a starvation scenario)
        while self.settled:
            meep = self.settled.popleft()
            # The meep may have died during their own turn, or as a consequence
            # of the actions of another meep who had a turn within the same
            # round.
            if meep.has_died:
                continue
            self.add_meep(
                meep=meep)
        return activity
    def _normalise_time_to_next_rung(self):
        '''We need the meep at the front of the priority list to have a fatigue
        of 0. Hence, we want adjust all the meeps in the queue by the fatigue
        of that first meep. Effectively, we are shift time to the point at
        which the meep would have 0 fatigue.'''
        fatigue = self.prio[0].fatigue
        if 0 == fatigue:
            return
        for meep in self.prio:
            meep.fatigue -= fatigue
    def __repr__(self):
        sb = []
        sb.append('  meep   fatigue')
        sb.append('  ==============')
        if not self.prio:
            sb.append('  [none]')
        for meep in self.prio:
            sb.append('  %s(%2s)  %s'%(meep.c, meep.overhead, meep.fatigue))
        sb.append('  ==============')
        sb.append('.')
        return '\n'.join(sb)

def initiative_new(sleep_per_tick):
    ob = Initiative(
        sleep_per_tick=sleep_per_tick)
    return ob


# --------------------------------------------------------
#   :testing
# --------------------------------------------------------
def test():
    import types
    def coords(s, e):
        ob = types.ModuleType('coords')
        ob.s = s
        ob.e = e
        return ob
    def create_fake_mind():
        class FakeMind(object):
            def __init__(self):
                pass
            def turn(self, meep):
                print('turn: %s (%s)'%(meep.c, meep.overhead))
            def waiting_for_input(self):
                return False
            def add_key(self, key):
                pass
        fake_mind = FakeMind()
        mind = mind_interface(
            cb_turn=fake_mind.turn,
            cb_add_key=fake_mind.add_key,
            cb_waiting_for_input=fake_mind.waiting_for_input)
        return mind
    mind = create_fake_mind()
    ts = initiative_new()
    ts.add_meep(
        meep=meep_new(
            mind=mind,
            coords=coords(
                s=0,
                e=0),
            c='a',
            overhead=5))
    ts.add_meep(
        meep=meep_new(
            mind=mind,
            coords=coords(
                s=0,
                e=0),
            c='b',
            overhead=8))
    ts.add_meep(
        meep=meep_new(
            mind=mind,
            coords=coords(
                s=0,
                e=0),
            c='c',
            overhead=10))
    ts.add_meep(
        meep=meep_new(
            mind=mind,
            coords=coords(
                s=0,
                e=0),
            c='d',
            overhead=7))
    ts.add_meep(
        meep=meep_new(
            mind=mind,
            coords=coords(
                s=0,
                e=0),
            c='e',
            overhead=9))
    ts.add_meep(
        meep=meep_new(
            mind=mind,
            coords=coords(
                s=0,
                e=0),
            c='f',
            overhead=12))
    ts.add_meep(
        meep=meep_new(
            mind=mind,
            coords=coords(
                s=0,
                e=0),
            c='g',
            overhead=2))
    def pause():
        print('[paused]', end='')
        input()
    def step():
        ts.dispatch_next_tick()
        print(str(ts))
        pause()
    print('-- initial ---------')
    print(str(ts))
    print('--------------------')
    pause()
    for i in range(20):
        step()

if __name__ == '__main__':
    test()

