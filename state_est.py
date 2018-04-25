import math
import cmath
import numpy as np
from utils import *
from reward import *
from MDP import *
from simulation import *

test_car = WRX(0, 0)

def est_shift_up(s, g):
  if len(test_car.gears) <= g:
    return g, s, 0, 0
  g = g + 1
  rpm = test_car.getRPM(s, g)
  hp = test_car.rpm_to_hp(rpm)
  return g, s, rpm, hp

def est_shift_down(s, g):
  if g <= 1:
    return g, s, 0, 0
  g = max(1, g - 1)
  rpm = test_car.getRPM(s, g)
  hp = test_car.rpm_to_hp(rpm)
  return g, s, rpm, hp

def est_braking(s, g, visible):
  slip_s = test_car.slip_speed(visible)
  if not slip_s:
    slip_s = s - 0.1
  s = max(slip_s, max(0, s - test_car.braking_dec))
  rpm = test_car.getRPM(s, g)
  hp = test_car.rpm_to_hp(rpm)
  return g, s, rpm, hp