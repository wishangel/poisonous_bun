# coding:utf-8
"""
ネズミ学習問題のQラーニングプログラム
Copyright(c) 2018 Koji Makino and Hiromitsu Nishizaki All Rights Reserved.
"""
import numpy as np
import argparse
import sys

 
def optimised_action(state):
    if state == 12:
        next_action = 0
    elif state % 4 == 0:
        next_action = np.random.choice([0, 1, 2])
    elif state % 4 == 1:
        next_action = 2
    elif state % 4 == 2:
        next_action = 1
    elif state % 4 == 3:
        next_action = 0
    return next_action

def random_action():
    return np.random.choice([0, 1, 2])
 
def get_action(state, episode, q_table, mode='ai'):
    epsilon = 10 * (1 / (episode + 1))
    while True:         #徐々に最適行動のみをとる、ε-greedy法
        if mode == 'ai':
            if epsilon <= np.random.uniform(0, 1):
                a = np.where(q_table[state]==q_table[state].max())[0]
                next_action = np.random.choice(a)
                next_state = state + next_action + 1
                if next_state <= 13:
                    break
            else:
                next_action = random_action()
                next_state = state + next_action + 1
                if next_state <= 13:
                    break
        elif mode == 'random':
            next_action = random_action()
            next_state = state + next_action + 1
            if next_state <= 13:
                break
        elif mode == 'human':
            next_action = optimised_action(state)
            break
        elif mode == 'cpu':
            a = np.where(q_table[state]==q_table[state].max())[0]
            next_action = np.random.choice(a)
            next_state = state + next_action + 1
            if next_state > 13:
                next_action = 0
            break
        else:
            next_action = random_action()
            next_state = state + next_action + 1
            if next_state <= 13:
                break
    return next_action

def play(state, action):
    hasFinished = False
    if action == 0:
        state += 1
    elif action == 1:
        state += 2
    else:
        state += 3
    if state >= 13:
        hasFinished = True

    return state, hasFinished

def update_Qtable(q_table, state, action, reward, next_state):
    gamma = 0.9
    alpha = 0.5
    next_maxQ = max(q_table[next_state])
    q_table[state, action] = (1 - alpha) * q_table[state, action] +\
            alpha * (reward + gamma * next_maxQ)
   
    return q_table

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Learning poison bun game without human knowledge'
    )
    parser.add_argument('--learn', action='store_true', help='ai start to learn')

    args = parser.parse_args()
    
    if args.learn:
        max_number_of_steps = 13  #1試行の最大step数
        num_episodes = 1000 #総試行回数
        q_table_player = np.zeros((14, 3))
        q_table_opponent = np.zeros((14, 3))
        opponent_win = 0
        player_win = 0

        for episode in range(num_episodes):  #試行数分繰り返す
            state = 0
            reward_player = 0
            reward_opponent = 0
            previous_state = 0
            previous_action = 0

            for step in range(1, max_number_of_steps + 1):  #1試行のループ
                if step % 2 == 1:
                    action = get_action(state, episode, q_table_player, mode='human')
                else:
                    action = get_action(state, episode, q_table_opponent)
                next_state, hasFinished = play(state, action)
                print(state, action, hasFinished, next_state)
                if hasFinished:
                    if step % 2 == 1: #後攻が勝ったとき
                        opponent_win += 1
                        reward_player = -1
                        reward_opponent = 1
                        q_table_opponent = update_Qtable(q_table_opponent, previous_state, previous_action, reward_opponent, state)
                        q_table_player = update_Qtable(q_table_player, state, action, reward_player, next_state)
                    else: #先攻が勝ったとき
                        player_win += 1
                        reward_player = 1
                        reward_opponent = -1
                        q_table_opponent = update_Qtable(q_table_opponent, state, action, reward_opponent, next_state)
                        q_table_player = update_Qtable(q_table_player, previous_state, previous_action, reward_player, state)
                    break
                if step % 2 == 1:
                    q_table_player = update_Qtable(q_table_player, state, action, reward_player, next_state)
                else :
                    q_table_opponent = update_Qtable(q_table_opponent, state, action, reward_opponent, next_state)
                #q_table_player = update_Qtable(q_table_player, state, action, episode_reward_player, next_state)
                #q_table_opponent = update_Qtable(q_table_opponent, state, action, episode_reward_opponent, next_state)
                #if hasFinished:
                #    if step % 2 == 1:
                #        q_table_opponent = update_Qtable(q_table_opponent, previous_state, previous_action, reward_opponent, state)
                #    else:
                #        q_table_player = update_Qtable(q_table_player, previous_state, previous_action, reward_player, state)
                #    break
                previous_action = action
                previous_state = state
                state = next_state
            print('player win', player_win)
            print('opponent win', opponent_win)
            print(q_table_player)
            print(q_table_opponent)

        np.savetxt('QValuePlayer.txt', q_table_player)
        np.savetxt('QValueOpponent.txt', q_table_opponent)
    else:
        #game start
        print('これから毒饅頭ゲームをはじめます')
        print('あなたが先行です')
        hasFinished = False
        max_buns = 13
        state = 0
        q_table = np.loadtxt('QValueOpponent.txt')

        while not hasFinished:
            print('＝＝プレイヤーの番＝＝')
            print('あなたは何個食べますか？(1~3の中から入力)')
            num_of_buns = sys.stdin.readline()
            next_state, hasFinished = play(state, int(num_of_buns) - 1)
            print('食べたまんじゅうの数：', next_state)
            print('＝＝＝＝＝＝＝', "\n")
            if hasFinished:
                print('あなたの負けです。')
                break
            state = next_state
            print('＝＝CPUの番＝＝')
            action = get_action(state, 10, q_table, mode='cpu')
            next_state, hasFinished = play(state, action)
            print('食べたまんじゅうの数：', next_state)
            print('＝＝＝＝＝＝＝', "\n")
            if hasFinished:
                print('あなたの勝ちです。')
                break
            state = next_state
