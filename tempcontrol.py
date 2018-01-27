import smbus,time
import RPi.GPIO as GPIO
class TempControl:
    pinList = [22,16,12,18,13,15]
    _state = [False]*6
    def __init__(self,a=0,units='C'):
        self.ltc2991 = smbus.SMBus(1)
        self.addr = 72+a
        self.units = units.capitalize()[0]
        if self.units not in 'CKF':
            print "Bad unit: %s"%(units)
        self.ltc2991.write_byte_data(self.addr,6,34)
        self.ltc2991.write_byte_data(self.addr,7,34)
        self.ltc2991.write_byte_data(self.addr,8,16)
        self.ltc2991.write_byte_data(self.addr,1,248)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.pinList,GPIO.OUT,initial=GPIO.LOW)
        
    def __del__(self):
        GPIO.cleanup()
        self.ltc2991.close()
        
    def waitBusy(self):
        while (self.ltc2991.read_byte_data(self.addr,1) & 4):
            pass
    def rawToCelsius(self,raw):
        # bytes are swapped in raw, msb is a "new data" flag
        # and remaining value uses twos-complement for negatives
        return ((raw/256+((raw&63)-(raw&64))*256)/16.0)

    def formatTemp(self,raw):
        c = self.rawToCelsius(raw)
        if self.units == 'C':
            return (c)
        if self.units == 'K':
            return (c+273.125)
        if self.units == 'F':
            return (c*1.8+32)
        
    def readTemp(self,channel):
#        self.ltc2991.write_byte_data(self.addr,1,248)
#        time.sleep(1)
        raw = self.ltc2991.read_word_data(self.addr,6+4*channel)
        return(self.formatTemp(raw))

    def readInternalTemp(self):
        return(self.readTemp(5))

    def setRelayState(self,relayNum,state):
        self._state[relayNum-1] = state
        value = GPIO.HIGH if state else GPIO.LOW
        GPIO.output(self.pinList[relayNum-1], value)

    def setRelayOn(self,relayNum):
        self.setRelayState(relayNum,True)

    def setRelayOff(self,relayNum):
        self.setRelayState(relayNum,False)

    def getRelayState(self,relayNum):
        return(self._state[relayNum-1])
