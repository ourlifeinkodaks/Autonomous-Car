import math
import cmath
import numpy as np
#import matplotlib.pyplot as plt #temp



#Environment Constants
step = 10 # meters
air_dens = 1.225 # kg/m^3
gravity = 9.8 # m/s^2


def alt_delta(steps):
  return (sum((float(step[0]) for step in steps))/len(steps))

# average turn angle of visible track ahead
def ang_delta(steps):
  return (sum((float(step[1]) for step in steps))/len(steps))




class WRX(object):
  gears = [3.17, 1.88, 1.3, 0.97, 0.74] # 5 gears
  final_drive = 3.9 # Final Drive Ratio
  tire_diameter = 0.65278 # meters, 25.3 inches: stock 17" wheels
  tire_radius = tire_diameter / 2
  idle_rpm = 750
  redline_rpm = 6300
  weight = 1511.823 #kg = 3333 lbs
  rolling_resistance = 0.02 # average rr constant
  drag_coef = 0.35
  front_area = 2.043866 # 22 * 0.092903 sqare feet converted to square meters
  length = 4.4196 # meters = 174 inches
  tran_efficiency = 0.8 # estimated, but realistic
  braking_dec = 0.83 * step #meters per second
  pk_rpm = 3510


  CUR_GEAR = 1 # Not starting at 0 because that would be confusing, starting at 1
  RPM = idle_rpm # init to idle
  MPS = 0 # starting from a stop
  
  # RPM, Newtons of Torque
  car_data = np.array([
    (1013, 159),
    (1496, 185),
    (2019, 236),
    (2525, 320),
    (3015, 352),
    (3510, 380),
    (3815, 373),
    (4008, 370),
    (4213, 368),
    (4513, 360),
    (5015, 354),
    (5523, 333),
    (5812, 326),
    (6014, 306),
    (6211, 286),
  ])
  rpms = car_data[:,0]
  trqs = car_data[:,1]
  z = np.polyfit(rpms, trqs, 3)
  dfunc = np.poly1d(z)
  fit_rpms = np.linspace(rpms[0], rpms[-1], 1000)
  fit_trqs = dfunc(fit_rpms)
  # plt.plot(rpms, trqs, 'o', fit_rpms, fit_trqs)
  # plt.show()



  def __init__(self, ALT, ANG):
    self.ALT = ALT
    self.ANG = ANG
  def setVals(self, MPS, RPM, CUR_GEAR):
    self.RPM = RPM

    self.MPS = MPS
    self.CUR_GEAR = CUR_GEAR

  def getRPM(self, MPS, CUR_GEAR):
    return (MPS/self.tire_radius) * self.gears[CUR_GEAR - 1] * self.final_drive * self.tran_efficiency * 60/(2 * math.pi)

  def getMPS(self, RPM, CUR_GEAR):
    return (RPM*self.tire_radius)/(self.gears[CUR_GEAR-1]*self.final_drive*self.tran_efficiency * 60/(2 * math.pi))

  def rpm_to_trq(self, rpm):
    return self.fit_trqs[(np.abs(self.fit_rpms-rpm)).argmin()]

  def rpm_to_hp(self, rpm):
    return self.rpm_to_trq(rpm) * rpm / 5252

  def grade(self, alt):
    return float(gravity) * float(alt)

  def wheel_torque(self, rpm, CUR_GEAR):
    return (self.rpm_to_trq(rpm) * self.gears[CUR_GEAR - 1] * self.final_drive * self.tran_efficiency) / self.tire_radius

  def drag(self, mps):
    return (0.5 * self.drag_coef * self.front_area * air_dens * (mps * mps)) + (self.rolling_resistance * mps)

  def acceleration(self, RPM, MPS, CUR_GEAR, alt):
    if RPM < self.idle_rpm:
      return 0.001
    force = self.wheel_torque(RPM, CUR_GEAR) - self.drag(MPS) 
    return force / self.weight + self.grade(alt)

  def slip_speed(self, steps):
    angle = 90.0 * abs(ang_delta(steps))
    if angle == 0.0:
      return False
    radius = 2*self.length / (math.sin(math.radians(angle)))
    return math.sqrt(radius)


  def slip(self, ang, MPS):
    angle = 90.0 * abs(float(ang))
    if angle == 0.0: # eliminate divide by 0
      return False
    radius = 2*self.length / (math.sin(math.radians(angle)))
    lat_force = (self.weight * (MPS * MPS)) / radius
    return lat_force >= self.weight


  def time_between(self, a, s, d):
    discRoot = math.sqrt((s * s) - 4 * a * d) # first pass
    root1 = (-s + discRoot) / (2 * a) # solving positive
    #root2 = (-s - discRoot) / (2 * a) # solving negative
    pos = "%.2f" % root1
    #neg = "%.2f" % root2
    return pos

  def next_speed(self, time, acc, s):
    return s + acc * float(time)

  def peak_trq(self, CUR_GEAR):
    return max((self.wheel_torque(d[0], CUR_GEAR) for d in self.car_data))
  
  def peak_hp(self):
    return max((self.rpm_to_hp(rpm) for rpm in self.fit_rpms))



