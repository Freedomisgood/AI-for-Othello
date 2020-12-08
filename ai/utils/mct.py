# -*- coding: utf-8 -*-
# @Time    : 2020/12/5 17:51
# @Author  : Mrli
# @FileName: main.py
# @Blog    : https://nymrli.top/
from enum import Enum
from random import choice
from time import time
from copy import deepcopy

import numpy as np


from board import Board
from config import C


class Chess(Enum):
    BLACK = {'graph': 'X', 'val': 0}
    WHITE = {'graph': 'O', 'val': 1}

    @staticmethod
    def getChess(color):
        for c in Chess:
            if color == c.value.get("graph"):
                return c

    def getVal(self):
        return self.value.get('val')

    def getGraph(self):
        return self.value.get('graph')


def game_over(board: Board):
    """
    判断游戏是否结束
    :return: True/False 游戏结束/游戏没有结束
    """
    # 根据当前棋盘，判断棋局是否终止
    b_list = list(board.get_legal_actions('X'))
    w_list = list(board.get_legal_actions('O'))
    return len(b_list) == 0 and len(w_list) == 0  # 返回值 True/False


def get_corner_score(board: Board, color: str):
    value = 0
    corners = (board[0][0], board[0][7], board[7][0], board[7][7],)
    for c in corners:
        if c == color:
            value += int(c == color)
        elif c == '.':
            value += 0
        else:
            value -= 1
    return value


def is_terminal(board: Board, color: str):
    """
    判断选手是否还能下棋
    如果当前选手没有合法下棋的位子，则切换选手；如果另外一个选手也没有合法的下棋位置，则比赛停止。
    :param board:
    :param color:
    :return:
    """
    moves = list(board.get_legal_actions(color))
    return len(moves) == 0


class Node():
    def __init__(self, color: Chess, board: Board, move=None, parent=None):
        self.chess = color  # 根据get_winner结果来设定的
        self.board = board
        self.parent = parent
        self._move = move
        self.untried_actions = list(self.board.get_legal_actions(self.chess.getGraph()))
        self.child = []
        self.vis = 0
        self.val = 0

    def get_move(self):
        return self._move

    def rollout(self):
        """
        随机模拟直到游戏结束, 并返回这个叶子节点的价值
        :return:
        """
        tempBoard = deepcopy(self.board)
        # color = self.chess.getGraph()
        color = Chess.WHITE.getGraph() if \
            self.chess.getGraph() == Chess.BLACK.getGraph() else Chess.BLACK.getGraph()
        while not game_over(tempBoard):
            possible_move = list(tempBoard.get_legal_actions(color))
            if possible_move:
                tempBoard._move(choice(possible_move), color)
            # else:
            #     print("-"*20)
            #     print("X:", len(list(tempBoard.get_legal_actions('X'))), "O:", \
            #               len(list(tempBoard.get_legal_actions('O'))))
            #     print(color, possible_move)
            #     tempBoard.display()
            #     print("-"*20)
            color = Chess.WHITE.getGraph() if \
                color == Chess.BLACK.getGraph() else Chess.BLACK.getGraph()

        # print("Winner:", tempBoard.get_winner())
        # V1. 如果赢了+1, 输了或者平局为0
        corner_v = get_corner_score(tempBoard, self.chess.getGraph())
        # print("corner_v:", corner_v)
        return int(tempBoard.get_winner()[0] == self.chess.getVal()) + corner_v / 4

    def backpropagate(self, value):
        """
        从子节点将结果传递到父节点, 更新一路上所有节点的N和v
        :param value:
        :return:
        """
        # if self.parent:       # 最好这么写
        #     self.parent.backpropagate(result)  
        pNode = self
        while pNode:        # 这样的写法忽视了private权限
            pNode.vis += 1
            pNode.val += value
            pNode = pNode.parent

    def extend(self):
        """
        从当前节点往子节点拓展
        :return:
        """
        move = choice(self.untried_actions)
        self.untried_actions.remove(move)
        tempBoard = deepcopy(self.board)
        tempBoard._move(move, self.chess.getGraph())
        childNode = Node(self.chess, tempBoard, move, self)
        self.child.append(childNode)
        return childNode

    def is_fully_expanded(self):
        """
        判断这个的子节点是否全被遍历过了
        :return:
        """
        return len(self.untried_actions) == 0

    def best_child(self, c_param=C):
        """
        得到根节点root来看当前UCB值最高的childNode
        :param c_param:
        :return:
        """
        choices_weights = [
            (c.val / c.vis) + c_param * np.sqrt((2 * np.log(self.vis) / c.vis))
            for c in self.child
        ]
        if not choices_weights:
            print("choices_weights")
        return self.child[np.argmax(choices_weights)]


class MCT():
    def __init__(self, play_color, limit_time):
        self.chess = Chess.getChess(play_color)
        self.limit_time = limit_time

    def search(self, board):
        """
        MCTS框架主逻辑
        :param board: 实时的真实棋盘
        :return:
        """
        root = Node(self.chess, board)

        begin = time()
        now = time()
        cnt = 0
        while now - begin < self.limit_time:
            # 1. 获得UCB最高的子节点进行最佳搜索->叶子节点vNode
            exNode = self._tree_policy(root)
            # 2. 从vNode开始进行rollout, 获得rollout结果
            value = exNode.rollout()
            # print("-"*20, value, "-"*20)
            # 3. 从vNode往上直到根节点root进行BP更新所有信息, V值和N值
            exNode.backpropagate(value)
            now = time()
            cnt += 1
        print("MCTS cacluted {} times".format(cnt))
        # 满足退出条件之后， 在root当前所有的child节点中找出value最高的childNode, 返回它的action
        return self.do_best_action(root)

    def do_best_action(self, root):
        """
        得到根节点root来看当前UCB值最高的childNode, 最后返回其move
        :param root:
        :return:
        """
        node = root.best_child(c_param=0)
        return node.get_move()

    def _tree_policy(self, root):
        """
        进行树的遍历
        :param root:
        :return:
        """
        v = root            # 所有v节点都是我方走的state
        # TODO: 从while not game_over(v.board): 改为了下面, 如果不能走的话就结束
        while not is_terminal(v.board, v.chess.getGraph()):  # 一直探索到游戏结束。在游戏未完全结束的时候每次会从v.extend退出
            if not v.is_fully_expanded():
                # 如果v还没遍历完的话，那么就继续从左往右依次遍历其子节点
                return v.extend()
            else:
                # 如果遍历完了v的所有子节点，则找出UCB最大的子节点继续进行最佳搜索
                v = v.best_child()
        return v


