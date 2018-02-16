# -*- coding: utf-8 -*-
# %matplotlib inline

import numpy as np
np.set_printoptions(suppress=True)

from shutil import copyfile
import random


from keras.utils import plot_model

from libs.ads import Game, GameState
from libs.ads.agent import Agent
from libs.ads.memory import Memory
from libs.ads.model import Residual_CNN
from libs.ads.funcs import playMatches, playMatchesBetweenVersions

import loggers as lg

import config

from settings import run_folder, run_archive_folder
from libs.ads.initialise import INITIAL_RUN_NUMBER, INITIAL_MODEL_VERSION, INITIAL_MEMORY_VERSION
import pickle

lg.logger_main.info('=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*')
lg.logger_main.info('=*=*=*=*=*=*      NEW LOG       =*=*=*=*=*')
lg.logger_main.info('=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*')

env = Game()

# If loading an existing neural network, copy the config file to root
#if INITIAL_RUN_NUMBER != None:
    #copyfile(run_archive_folder + env.name + '/run' + str(INITIAL_RUN_NUMBER).zfill(4) + '/config.py', './config.py')

if INITIAL_MEMORY_VERSION == None:
    memory = Memory(config.MEMORY_SIZE)

current_NN = Residual_CNN(config.REG_CONST, config.LEARNING_RATE, (2,) + env.grid_shape,   env.action_size, config.HIDDEN_CNN_LAYERS)
best_NN = Residual_CNN(config.REG_CONST, config.LEARNING_RATE, (2,) +  env.grid_shape,   env.action_size, config.HIDDEN_CNN_LAYERS)

best_player_version = 0
best_NN.model.set_weights(current_NN.model.get_weights())

copyfile('./config.py', run_folder + 'config.py')
plot_model(current_NN.model, to_file=run_folder + 'models/model.png', show_shapes = True)

current_player = Agent('current_player', env.state_size, env.action_size, config.MCTS_SIMS, config.CPUCT, current_NN)
best_player = Agent('best_player', env.state_size, env.action_size, config.MCTS_SIMS, config.CPUCT, best_NN)
iteration = 0

while True:
    iteration += 1
    reload(lg)
    reload(config)

    print('ITERATION NUMBER ' + str(iteration))
    print('BEST PLAYER VERSION ' + str(best_player_version))
    print('SELF PLAYING ' + str(config.EPISODES) + ' EPISODES...')
    print('\n')
    lg.logger_main.info('BEST PLAYER VERSION: %d', best_player_version)
    
    _, memory, _, _ = playMatches(best_player, best_player, config.EPISODES, lg.logger_main, turns_until_tau0 = config.TURNS_UNTIL_TAU0, memory = memory)
    memory.clear_stmemory()
    if len(memory.ltmemory) >= config.MEMORY_SIZE:
        print('RETRAINING')
        current_player.replay(memory.ltmemory)
    
    if iteration % 5 == 0:
        pickle.dump( memory, open( run_folder + "memory/memory" + str(iteration).zfill(4) + ".p", "wb" ) )
    
    lg.logger_memory.info('====================')
    lg.logger_memory.info('NEW MEMORIES')
    lg.logger_memory.info('====================')

    memory_samp = random.sample(memory.ltmemory, min(1000, len(memory.ltmemory)))
    for s in memory_samp:
        current_value, current_probs, _ = current_player.get_preds(s.get('state'))
        best_value, best_probs, _ = best_player.get_preds(s.get('state'))
       
        lg.logger_memory.info('MCTS VALUE FOR %s: %f', s['playerTurn'], s['value'])
        lg.logger_memory.info('CUR PRED VALUE FOR %s: %f', s['playerTurn'], current_value)
        lg.logger_memory.info('BES PRED VALUE FOR %s: %f', s['playerTurn'], best_value)
        lg.logger_memory.info('THE MCTS ACTION VALUES: %s', ['%.2f' % elem for elem in s['AV']]  )
        lg.logger_memory.info('CUR PRED ACTION VALUES: %s', ['%.2f' % elem for elem in  current_probs])
        lg.logger_memory.info('BES PRED ACTION VALUES: %s', ['%.2f' % elem for elem in  best_probs])
        lg.logger_memory.info('ID: %s', s['state'].id)
        lg.logger_memory.info('INPUT TO MODEL: %s', current_player.model.convertToModelInput(s['state']))

        s['state'].render(lg.logger_memory)

    print('TOURNAMENT...')
    scores, _, _points, sp_scores = playMatches(best_player, current_player, config.EVAL_EPISODES, lg.logger_tourney, turns_until_tau0 = 0, memory = None)
    print('\nSCORES')
    print(scores)
    print('\nSTARTING PLAYER / NON-STARTING PLAYER SCORES')

    print('\n\n')
    
    if scores['current_player'] > scores['best_player'] * config.SCORING_THRESHOLD:
        best_player_version = best_player_version + 1
        best_NN.model.set_weights(curent_NN.model.get_weights())
        best_NN.write(env.name, best_player_version)

    else:
        print('MEMORY SIZE: ' + str(len(memory.ltmemory)))
