#!/usr/local/midas/bin/python

"""PrecisionTime.py is a collection of python classes to manipulate times with high
precision using integer logic.

Written by "Bill Rideout":mailto:wrideout@haystack.mit.edu  May 24, 2007

$Id$
"""
import types

class nsTime:
    """nsTime is a class to handle times given as UT second (integer) and nanosecond (integer)

    If nanosecond > 1E9, seconds will be added to second
    """

    def __init__(self, second, nanosecond):
        self.second = int(second)
        if self.second < 0:
            raise ValueError, 'seconds must be greater than 0, not %i' % (self.second)
        nanosecond = long(nanosecond)
        if nanosecond < 0:
            raise ValueError, 'nanoseconds must be greater 0, not %i' % (nanosecond)
        addSec = nanosecond / 1000000000
        if addSec > 0:
            self.second += addSec
        self.nanosecond = nanosecond % 1000000000
        self.totalNS = long(self.nanosecond) + long(self.second) * 1000000000
        

    def __add__(self, other):
        """__add__ another nsTime to this one and return a new one as result
        """
        nsResult = self.nanosecond + other.nanosecond
        addSec = int(nsResult / 1000000000)
        newSec = self.second + other.second + addSec
        newNS = nsResult % 1000000000
        return(nsTime(newSec, newNS))
    

    def increase(self, other):
        """increase adds other to self, changing self (rather than creating a new object)
        """
        nsResult = self.nanosecond + other.nanosecond
        addSec = int(nsResult / 1000000000)
        self.second = self.second + other.second + addSec
        self.nanosecond = nsResult % 1000000000
        self.totalNS = long(self.nanosecond) + long(self.second) * 1000000000
    

    def __sub__(self, other):
        """__sub__ another nsTime from this one and return a new one as result
        """
        nsResult = self.nanosecond - other.nanosecond
        if nsResult < 0:
            addSec = 1
            nsResult += 1000000000
        else:
            addSec = 0
        newSec = (self.second - other.second) - addSec
        return(nsTime(newSec, nsResult))
    

    def multiply(self, factor):
        """multiply this nsTime times an integer
        """
        if type(factor) not in (types.IntType, types.LongType):
            raise ValueError, 'Illegal type %s passed into nsTime.multiply' % (str(type(factor)))
        newTotalNS = self.totalNS * factor
        newSeconds = int(newTotalNS / 1000000000)
        newNanoseconds = int(newTotalNS - (newSeconds * 1000000000))
        return(nsTime(newSeconds, newNanoseconds))
    

    def integerDivision(self, other):
        """integerDivision returns the total number of other nsTimes that fit in self
        """
        return(int(self.totalNS / other.totalNS))

    def getUnixTime(self):
        """ getUnixTime() returns a Unix style time as a float. """
        return(float(self.second) + float(self.nanosecond)/1.0e9)

    def __mod__(self, other):
        """__mod__ implements self % other.
        """
        if type(other) in (types.IntType, types.LongType):
            return self.totalNS % other
        else:
            return self.totalNS % other.totalNS
    
    def __eq__(self, other):
        """ equality of two nsTime objects """
        if not (hasattr(other, 'second') and hasattr(other, 'nanosecond')): return False
        return self.__cmp__(other) == 0
    
    def __cmp__(self, other):
        """compare two nsTime objects
        """
        result = cmp(self.second, other.second)
        if result != 0:
            return(result)

        return(cmp(self.nanosecond, other.nanosecond))


    def __str__(self):
        return '%d.%09d' % (self.second, self.nanosecond)
    
    
class psTime:
    """psTime is a class to handle times given as UT second (integer) and picosecond (integer)

    If picosecond > 1E12, seconds will be added to second
    """

    def __init__(self, second, picosecond):
        self.second = int(second)
        if self.second < 0:
            raise ValueError, 'seconds must be greater than 0, not %i' % (self.second)
        picosecond = long(picosecond)
        if picosecond < 0:
            raise ValueError, 'picoseconds must be greater 0, not %i' % (picosecond)
        addSec = picosecond / 1000000000000
        if addSec > 0:
            self.second += addSec
        self.picosecond = picosecond % 1000000000000
        self.totalPS = long(self.picosecond) + long(self.second) * 1000000000000
        

    def __add__(self, other):
        """__add__ another psTime to this one and return a new one as result
        """
        psResult = self.picosecond + other.picosecond
        addSec = int(psResult / 1000000000000)
        newSec = self.second + other.second + addSec
        newPS = psResult % 1000000000000
        return(psTime(newSec, newPS))
    

    def increase(self, other):
        """increase adds other to self, changing self (rather than creating a new object)
        """
        psResult = self.picosecond + other.picosecond
        addSec = int(psResult / 1000000000000)
        self.second = self.second + other.second + addSec
        self.picosecond = psResult % 1000000000000
        self.totalPS = long(self.picosecond) + long(self.second) * 1000000000000
    

    def __sub__(self, other):
        """__sub__ another psTime from this one and return a new one as result
        """
        psResult = self.picosecond - other.picosecond
        if psResult < 0:
            addSec = 1
            psResult += 1000000000000
        else:
            addSec = 0
        newSec = (self.second - other.second) - addSec
        return(psTime(newSec, psResult))
    

    def multiply(self, factor):
        """multiply this psTime times an integer
        """
        if type(factor) not in (types.IntType, types.LongType):
            raise ValueError, 'Illegal type %s passed into psTime.multiply' % (str(type(factor)))
        newTotalPS = self.totalPS * factor
        newSeconds = int(newTotalPS / 1000000000000)
        newPicoseconds = int(newTotalPS - (newSeconds * 1000000000000))
        return(psTime(newSeconds, newPicoseconds))
    

    def integerDivision(self, other):
        """integerDivision returns the total number of other psTimes that fit in self
        """
        return(int(self.totalPS / other.totalPS))

    def getUnixTime(self):
        """ getUnixTime() returns a Unix style time as a float. """
        return(float(self.second) + float(self.picosecond)/1.0e12)

    def __mod__(self, other):
        """__mod__ implements self % other.
        """
        if type(other) in (types.IntType, types.LongType):
            return self.totalPS % other
        else:
            return self.totalPS % other.totalPS
    
    def __eq__(self, other):
        """ equality of two psTime objects """
        if not (hasattr(other, 'second') and hasattr(other, 'picosecond')): return False
        return self.__cmp__(other) == 0

    def __cmp__(self, other):
        """compare two psTime objects
        """
        result = cmp(self.second, other.second)
        if result != 0:
            return(result)

        return(cmp(self.picosecond, other.picosecond))


    def __str__(self):
        return '%d.%12d' % (self.second, self.picosecond)
         

