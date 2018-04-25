from utils import *
from reward import *
from MDP import * 


ALT = 0 # assumes starting at 0 alt
ANG = 0.0 # always starting strait

car = WRX(ALT, ANG)
def simulate(track, lap):
  total_time = 0.0 #s
  record = []
  for i in range(len(track)):
    try:
      action = lap[i]
      section = [track[i]]
      alt = section[0][0]
      # current values 
      c_rpm = car.RPM
      c_s = car.MPS
      c_g = car.CUR_GEAR
      acc = car.acceleration(c_rpm, c_s, c_g, alt)
      time = car.time_between(acc / 2, c_s, -(step))
      
      if car.slip(section[0][1], c_s):
        record.append((c_rpm, c_s, c_g, True, False))
        total_time = -1
        break
      if c_rpm < car.idle_rpm:
        record.append((c_rpm, c_s, c_g, False, True))
        total_time = -2
        break
      record.append((c_rpm, c_s, c_g, False, False))

      
      
      # new values
      if action == "up":
        n_g = min(len(car.gears), c_g + 1)
      elif action == "down":
        n_g = max(1, c_g - 1)
      elif action == "brake":
        n_s = max(0, c_s - car.braking_dec)
        n_rpm = car.getRPM(n_s, c_g)
        n_g = c_g
        acc = car.acceleration(n_rpm, n_s, n_g, alt)
        time = car.time_between(acc / 2, n_s, -(step))
        car.setVals(n_s, n_rpm, n_g)
        total_time += float(time)
        continue
      else:
        n_g = c_g

      
      
      
      total_time += float(time)
      n_s = car.next_speed(time, acc, c_s)
      n_rpm = car.getRPM(n_s, n_g)
      if n_rpm > car.redline_rpm:
        car.setVals(car.getMPS(car.redline_rpm, n_g), car.redline_rpm, n_g)
        continue
      car.setVals(n_s, n_rpm, n_g)
    except IOError:
      pass # I know...I know
  car.setVals(0, car.idle_rpm, 1)
  return total_time, record