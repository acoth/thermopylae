import time,tempcontrol,sqlite3

tc = tempcontrol.TempControl(units='F')


db_file = '/home/pi/thermopylae/temp_db.sqlite'
db_table = 'temps'

db = sqlite3.connect(db_file)
c = db.cursor()

prevSampleTime = 0
try:
    while 1:
        subRec = list()
        for n in range(32):
            subRec.append([tc.readTemp(x+1) for x in range(5)])
            time.sleep(1)
        transpose = zip(*subRec)
        means = [sum(x)/len(x) for x in transpose]
        states = [1 if tc.getRelayState(x+1) else 0 for x in range(6)]
        c.execute("INSERT INTO temps (time, water_temp, pipe_temp, aux1_temp, aux2_temp, air_temp, state1, state2, state3, state4, state5, state6) VALUES (CURRENT_TIMESTAMP, %s, %s)"%(str(means)[1:-1],str(states)[1:-1]))
        db.commit()
        water_temp = means[0]
        setpoint, offset, pipeMeltHi, pipeMeltLo = c.execute("SELECT setpoint, offset, pipeMeltHi, pipeMeltLo FROM control").fetchone()
        aux2_temp = means[3]
        if (water_temp > (setpoint+offset)):
            tc.setRelayOff(1)
        if (water_temp < (setpoint-offset)):
            tc.setRelayOn(1)    
        if (aux2_temp > pipeMeltHi):
            tc.setRelayOff(2)
        if (aux2_temp < pipeMeltLo):
            tc.setRelayOn(2)
finally:
    c.close()
    db.close()
