#!/usr/bin/env python
from __future__ import division

import pygame # graphics

import json # to read world files
import random
import math
import sys

recording = False
if len(sys.argv) > 1:
  recording = True

global world
world = None

CELL_SIZE = 2
GRID_WIDTH = 512+2
GRID_HEIGHT = 512+2

GFX_WIDTH = 512
GFX_HEIGHT = 512
ONSCREEN_WIDTH = GFX_WIDTH//CELL_SIZE
ONSCREEN_HEIGHT = GFX_HEIGHT//CELL_SIZE

the_grid = [[(i+j)%2 for j in range(GRID_HEIGHT)] for i in range(GRID_WIDTH)]
the_grid_buffer = [[(i+j)%2 for j in range(GRID_HEIGHT)] for i in range(GRID_WIDTH)]
LIVE_CELL_ENUM = 2
DIRECTIONS = [(0,-1), (0,1), (-1,0), (1,0)]
OPP_DIR = {0:1, 1:0, 2:3, 3:2}

class World(object):
  def __init__(self, world_dims, geom_list, ball_radius, t_coll, timestep_size, ball_traj, hit_block):
    self.geom_list = geom_list
    self.ball_radius = ball_radius
    self.t_coll = t_coll
    self.world_dims = world_dims
    self.timestep_size = timestep_size
    self.ball_traj = ball_traj
    self.ball_gfx = self.gen_ball_gfx()
    self.geom_gfx = self.gen_geom_gfx()
    self.hit_block = hit_block

  def gen_ball_gfx(self):
    rad = self.ball_radius
    dims = self.coords_to_gfxcoords((2*rad,2*rad))
    ball_gfx = pygame.Surface(dims)
    #ball_gfx.fill((255,255,0))
    #pygame.draw.circle(ball_gfx, (255,128,76), (dims[0]//2,dims[1]//2), dims[0]//2)
    ball_gfx.fill((128,128,255))
    #pygame.draw.circle(ball_gfx, (255,255,155), (dims[0]//2,dims[1]//2), dims[0]//2)
    return ball_gfx

  def gen_geom_gfx(self):
    #if not cached yet
    geom_gfx = []
    for i,block in enumerate(self.geom_list):
      x0,y0,x1,y1 = block
      x0,y0 = self.coords_to_gfxcoords((x0,y0))
      x1,y1 = self.coords_to_gfxcoords((x1,y1))
      block_gfx = pygame.Surface((x1-x0,y1-y0))
      if i==0:
        block_gfx.fill((255,0,0))
      elif i==1:
        block_gfx.fill((0,255,0))
      else:
        block_gfx.fill((0,0,0))
      geom_gfx.append(block_gfx)

    return geom_gfx

  def coords_to_gfxcoords(self, coords):
    x,y = coords
    x *= GFX_WIDTH / self.world_dims[0]
    y *= GFX_HEIGHT / self.world_dims[1]
    return (int(x),int(y))

  def gfxcoords_to_coords(self, gfxcoords):
    x,y = gfxcoords
    x /= GFX_WIDTH / self.world_dims[0]
    y /= GFX_HEIGHT / self.world_dims[1]
    return (x,y)

def make_world_from_json(world_json):
  world_dims = world_json['world_dims']
  geom_list = world_json['geom_list']
  ball_radius = world_json['ball_radius']
  t_coll = world_json['t_coll']
  timestep_size = world_json['timestep_size']
  ball_traj = world_json['ball_traj']
  hit_block = world_json['hit_block']
  return World(world_dims, geom_list, ball_radius, t_coll, timestep_size, ball_traj, hit_block)

# define a main function
def main():

  # initialize the pygame module
  pygame.init()
  pygame.font.init()
  
  # call the main function
##  world_json = json.load(open('data/world1.json','r'))
##  world_grid_json = json.load(open('data/worldGrid.json','r'))

  conn = random.random() < .4;
  fname = 'helloWorld.json'
  if conn:
    fname = 'dataWorldsC/world' + str(int(random.random()*1000))+'.json'
  else:
    fname = 'dataWorldsD/world' + str(int(random.random()*1000))+'.json'
  print(fname)

##  batch = json.load(open(fname,'r'))
##  world_json = batch.get('world')
##  world_grid_json = batch.get('world_grid')
  
  batch = json.load(open('dataWorldsC/world88.json','r'))
  world_json = batch.get('world')
  world_grid_json = batch.get('world_grid')
  
  world = make_world_from_json(world_json)
  print (world.world_dims)
  print (world.coords_to_gfxcoords((100,100)))
  print (world.gfxcoords_to_coords((512,512)))
  print (len(world.ball_traj) * world.timestep_size)
  print (world.ball_traj[0])

  world_grid = world_grid_json['world_grid']
  cell_size = world_grid_json['cell_size']
  
  # set up some GFX
  cell_dims = world.coords_to_gfxcoords((cell_size,cell_size))

  grid_filled_gfx = pygame.Surface(cell_dims);
  grid_filled_gfx.fill((255,255,0))
  pygame.draw.rect(grid_filled_gfx, (0,0,0), (0,0,cell_dims[0],cell_dims[1]), 1)

  grid_empty_gfx = pygame.Surface(cell_dims)
  grid_empty_gfx.fill((255,255,255))
  pygame.draw.rect(grid_empty_gfx, (0,0,0), (0,0,cell_dims[0],cell_dims[1]), 1)

  grid_special_gfx = pygame.Surface(cell_dims)
  grid_special_gfx.fill((0,0,255))
  pygame.draw.rect(grid_special_gfx, (0,0,0), (0,0,cell_dims[0],cell_dims[1]), 1)

  grid_img = pygame.Surface((GFX_WIDTH,GFX_HEIGHT));
  grid_img.fill((0,0,0))
  for i in range(len(world_grid)):
      for j in range(len(world_grid[i])):
        #x,y = j*cell_dims[1], i*cell_dims[0];
        x,y = world.coords_to_gfxcoords((j*cell_size, i*cell_size));
        if world_grid[i][j] == -1:
          grid_img.blit(grid_empty_gfx, (x,y))
        elif world_grid[i][j] in [0,1]:
          grid_img.blit(grid_special_gfx, (x,y))
        else:
          grid_img.blit(grid_filled_gfx, (x,y))

  my_font = pygame.font.SysFont("Ubuntu Mono", 30)
  score_text = my_font.render('Score: ', False, (128,128,128))
  score_num_text = None

  # load and set the logo
#  logo = pygame.image.load("logo32x32.png")
#  pygame.display.set_icon(logo)
  pygame.display.set_caption('Ball Bounce Viz')

  # create a surface on screen that has the size
  screen = pygame.display.set_mode((GFX_WIDTH,GFX_HEIGHT))

  # Set up input tracking
  all_keys_status = pygame.key.get_pressed()
  keys_status = {k:all_keys_status[k] for k in [pygame.K_m, pygame.K_z, pygame.K_g]}

  # define a variable to control the main loop
  running = True

  UPDATE_EVENT_ID = (pygame.USEREVENT + pygame.NUMEVENTS) // 2
  frame_length_ms = 10
  pygame.time.set_timer(UPDATE_EVENT_ID, int(frame_length_ms)) # update every arg2 milliseconds

  score_rate_ms = 50
  score_log_rate_ms = 300

  # main loop
  counter = 0
  counter_changed = False
  balltraj_counter = 0
  last_keyframe_count = 0
  gridmode_counter = 0
  current_scores = [0,0]
  timeseries_scores = [[0,0]]
  steps_in_new_keyframe = None
  while running:
    counter_changed = False
    just_hit = set()
    # event handling, gets all event from the eventqueue
    for event in pygame.event.get():
      # only do something if the event is of type QUIT
      if event.type == pygame.QUIT:
        # change the value to False, to exit the main loop
        running = False

      elif event.type == UPDATE_EVENT_ID:
        # Advance the ball along its trajectory
        counter += 1
        counter_changed = True

      elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
          if balltraj_counter >= len(world.ball_traj)-1:
##            print fname
##            ofname = 'human_trials/' + fname
##            out = open(ofname, 'w')
##            a={}
##            a['world'] = world_json
##            a['world_grid'] = world_grid_json
##            a['timeseries_scores'] = timeseries_scores
##            out.write(json.dumps(a))
##            out.write('\n')
##            out.close()
            pass
          return 0
        
        if event.key in keys_status:
          if not keys_status[event.key]:
            just_hit.add(event.key)
          keys_status[event.key] = True
        
      elif event.type == pygame.KEYUP:
        if event.key in keys_status:
          keys_status[event.key] = False
          #just_hit.add(event.key)

    ## HANDLE INPUT
    if pygame.K_g in just_hit:
      gridmode_counter += 1
      gridmode_counter %= 3

    if balltraj_counter < len(world.ball_traj)-1:
      if counter_changed and counter%int(score_rate_ms//frame_length_ms) == 0:
        if keys_status[pygame.K_m] and not keys_status[pygame.K_z]:
          current_scores[1] += 1
        if keys_status[pygame.K_z] and not keys_status[pygame.K_m]:
          current_scores[0] += 1
      if counter%int(score_log_rate_ms//frame_length_ms) == 0:
        timeseries_scores.append(current_scores)
  
    ## GRAPHICS
    screen.fill((255,255,255))

    if gridmode_counter==1:
      screen.blit(grid_img,(0,0))
    
    for i,block in reversed(list(enumerate(world.geom_list))):
      x0,y0,x1,y1 = block
      screen.blit(world.geom_gfx[i], world.coords_to_gfxcoords((x0,y0)))

    if gridmode_counter==2:
      screen.blit(grid_img,(0,0))

#    bx,by,bxv,byv = world.ball_traj[min(counter, len(world.ball_traj)-1)]
    ball = None
    if balltraj_counter >= len(world.ball_traj)-1:
      ball = world.ball_traj[balltraj_counter]
    elif steps_in_new_keyframe is not None and \
         counter < (last_keyframe_count+steps_in_new_keyframe):
      ball0 = world.ball_traj[balltraj_counter]
      ball1 = world.ball_traj[balltraj_counter+1]
##      frac = (counter-last_keyframe_count) / steps_in_new_keyframe
##      ball = [ball0[i]*(1-frac)+ball1[i]*(frac) for i in range(len(ball0[:2]))] + ball0[2:]
      t = (counter-last_keyframe_count)*frame_length_ms/1000
      ball = [ball0[i]+t*ball0[2+i] for i in range(len(ball0[:2]))] + ball0[2:]
    else: # update counters
      if steps_in_new_keyframe is not None:
        last_keyframe_count = counter
        balltraj_counter += 1

      ball0 = world.ball_traj[balltraj_counter]
      ball1 = world.ball_traj[min(balltraj_counter+1, len(world.ball_traj)-1)]
      dist = math.hypot(ball0[0]-ball1[0],ball0[1]-ball1[1])
      speed = math.hypot(ball0[2],ball0[3])
      steps_in_new_keyframe = int(math.floor((dist/speed) * 1000 / frame_length_ms))
      ball = ball0

    bx,by,bxv,byv = ball  
    screen.blit(world.ball_gfx, world.coords_to_gfxcoords((bx-world.ball_radius,by-world.ball_radius)))

    if balltraj_counter >= len(world.ball_traj)-1:
      screen.blit(score_text, (GFX_WIDTH//3, GFX_HEIGHT//4))
      if not score_num_text:
        score_num = current_scores[1-world.hit_block] - current_scores[world.hit_block]
        score_num_text = my_font.render(str(score_num), False, (128,128,128))
      screen.blit(score_num_text, (GFX_WIDTH//3+100, GFX_HEIGHT//4))
      
    
    pygame.draw.rect(screen, (255,0,0), (GFX_WIDTH//2+20, GFX_HEIGHT-20,max(0,int(current_scores[1])),10), 0)
    pygame.draw.rect(screen, (0,255,0), (GFX_WIDTH//2-20 - max(0,int(current_scores[0])), GFX_HEIGHT-20,max(0,int(current_scores[0])),10), 0)

    pygame.display.flip()

  #wend
  
# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
if __name__=="__main__":
  main()
