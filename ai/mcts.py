# -*- coding: utf-8 -*-
# @Time    : 2020/12/5 17:51
# @Author  : Mrli
# @FileName: main.py
# @Blog    : https://nymrli.top/
import sys
sys.path.append("..")

from .utils.mct import MCT
from config import THINK_TIME


class AIPlayer:
    """
    AI 玩家
    """

    def __init__(self, color):
        """
        玩家初始化
        :param color: 下棋方，'X' - 黑棋，'O' - 白棋
        """

        self.color = color
        self.mct = MCT(self.color, THINK_TIME)

    def get_move(self, board):
        """
        根据当前棋盘状态获取最佳落子位置
        :param board: 棋盘
        :return: action 最佳落子位置, e.g. 'A1'
        """
        if self.color == 'X':
            player_name = '黑棋'
        else:
            player_name = '白棋'
        print("请等一会，对方 {}-{} 正在思考中...".format(player_name, self.color))

        # -----------------请实现你的算法代码--------------------------------------

        action = self.mct.search(board)
        # ------------------------------------------------------------------------

        return action
