import sys
import csv
import json
from utils import *
from reward import *
from MDP import *
from simulation import *

# System Arguments
# reward, path to track file
if len(sys.argv) != 2:
  print("usage:\n        path to track file (required)")
  sys.exit()
else:
  track = []
  try:
    with open(sys.argv[1]) as csvfile:
      t = csv.reader(csvfile)
      for row in t:
        track.append(row)
  except IOError:
      print("COULD NOT FIND FILE")
      sys.exit() 

  
  sight = 10
  

  # init
  min_consensus = 10
  consensus = []
  lap = ["acc"] * len(track)
  time, record = simulate(track, lap)
  best = 0
  all_lap_times = []
  while len(consensus) < min_consensus:
    new_lap, kill = generate_lap(track, lap, record, car, sight)
    time, record = simulate(track, new_lap)
    all_lap_times.append(time)
    # The loop is meant to end when the simulation has plateaued, and no improvement is expected
    # The list 'consensus' keeps track of the best time, and keeps duplicate results until the minimum consensus is met
    if time < 0:
      # DNF
      time = -1
      continue
    elif len(consensus) == 0:
      #empty
      consensus.append(time)
      best = new_lap
    elif time < consensus[0]:
      # new best time
      consensus = [time]
      best = new_lap
    elif time == consensus[0]:
      # duplicate time, consistent
      consensus.append(time) 
    
    lap = new_lap
    if kill:
      break

  print("\nAll lap times:")
  print(all_lap_times)
  print("\nBest time: ")
  print(consensus)
  print("\nBest lap: ")
  print(filter(lambda x: not x=="acc", best))
  

sys.exit("End")