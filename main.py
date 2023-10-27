import pywinauto
import time
from datetime import datetime
import signal
import ctypes
import cv2
import numpy as np
import pyautogui
# import os
# from socket_msg import client

from nv_config import NV_INFO, DNP_CFG, NPC_CFG

MOUSEEVENTF_MOVE = 0x0001  # mouse move
MOUSEEVENTF_LEFTDOWN = 0x0002  # left button down
MOUSEEVENTF_LEFTUP = 0x0004  # left button up
MOUSEEVENTF_RIGHTDOWN = 0x0008  # right button down
MOUSEEVENTF_RIGHTUP = 0x0010  # right button up
MOUSEEVENTF_MIDDLEDOWN = 0x0020  # middle button down
MOUSEEVENTF_MIDDLEUP = 0x0040  # middle button up
MOUSEEVENTF_WHEEL = 0x0800  # wheel button rolled
MOUSEEVENTF_ABSOLUTE = 0x8000  # absolute move
DISCONNECT_MSG = "!DISCONNECT"


def spam_ordinates():
    ''' function to determin the mouse coordinates'''

    print('press "x" key to lock position...')
    pre_x = 0
    pre_y = 0
    while True:
        # Check if x key is pressed
        time.sleep(0.1)

        x, y = pyautogui.position()

        if x != pre_x or y != pre_y:
            print(f'spam at position: {x}, {y}')
            pass
        pre_x = x
        pre_y = y


class BaseAuto:
    def __init__(self, nv_info_key=''):
        self.NV_INFO = NV_INFO[nv_info_key]
        self.NAME_NV = self.NV_INFO['NV_NAME']
        self.PASS = self.NV_INFO['PASS']
        self.TK = self.NV_INFO['TK']
        self.PT_PATH = self.NV_INFO['PT_PATH']
        self.PT_NAME = self.NV_INFO['PT_NAME']
        self.config_name = nv_info_key
        self.x_pos = 0
        self.y_pos = 0

    def action(self,
               path_image_live,
               path_child_image,
               x_adjust,
               y_adjust,
               log_error='',
               debug=False,
               right_click=False,
               no_click=False,
               save_pos=True,
               x_pos=0,
               y_pos=0
               ):
        self.app.FSOnlineClass.set_focus()
        time.sleep(0.1)
        self.take_screen_shot(path_image_live)
        time.sleep(0.1)
        if x_pos == 0 and y_pos == 0:
            x_pos, y_pos = self.find_post_image(path_child_image, path_image_live)
            if x_pos is None:
                print(log_error)
                return False
            if debug is True:
                print(x_pos, y_pos)

            if no_click:
                return True
        x_pos, y_pos = self.adjust_pos(x_pos, y_pos, x_adjust, y_adjust)
        if not right_click:
            self.move_and_click_left(x_pos, y_pos)
        else:
            self.move_and_click_right(x_pos, y_pos)
        if save_pos:
            self.x_pos = x_pos
            self.y_pos = y_pos
        time.sleep(0.1)
        return True

    def adjust_pos(self, x_pos, y_pos, x_adjust, y_adjust):
        x_pos = x_pos + x_adjust
        y_pos = y_pos + y_adjust
        return x_pos, y_pos

    def take_screen_shot(self, path_image_live):
        # time.sleep(5)
        screen_shot = pyautogui.screenshot()
        screen_shot.save(path_image_live)

    def move_and_click_left(self, x_pos, y_post):
        ctypes.windll.user32.SetCursorPos(int(x_pos), int(y_post))
        ctypes.windll.user32.mouse_event(2, 0, 0, 0, 0)
        ctypes.windll.user32.mouse_event(4, 0, 0, 0, 0)

    def move_and_click_right(self, x_pos, y_post):
        ctypes.windll.user32.SetCursorPos(int(x_pos), int(y_post))
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)

    def init_game_windown(self, first_init=False, skip_delete_nv=False):
        print('Chay lai game')
        path_image_live = 'image/login/live_image/init_game_windown.png'

        self.app = pywinauto.application.Application().start(cmd_line=self.PT_PATH)
        time.sleep(1)
        is_success = False
        for idx in range(0, 100):
            is_success = self.action(path_image_live, 'image/login/login_init_game.png', 20, 10,
                                     log_error='init_game not found', no_click=True)
            if is_success:
                break
        if not is_success:
            exit(0)

        if first_init:
            pt_windows = pywinauto.findwindows.find_windows(title_re=self.PT_NAME)
        else:
            pt_windows = pywinauto.findwindows.find_windows(title_re=self.PT_NAME)
            for pt_window in pt_windows:
                self.app = pywinauto.application.Application().connect(handle=pt_window)
                is_success = self.action(path_image_live, 'image/login/login_init_game.png', 20, 10,
                                         log_error='init_game not found', no_click=True)
                if is_success:
                    break
        if not is_success:
            exit(0)
        print('Start game ......')
        self.app.FSOnlineClass.type_keys('{ENTER}')
        time.sleep(0.2)
        is_success = self.action(path_image_live, 'image/login/login_init_game_btn.png', 20, 10,
                                 log_error='init_game_btn not found')
        if not is_success:
            exit(0)
        time.sleep(0.2)
        is_success = self.action(path_image_live, 'image/login/login_chon_server.png', 20, 10,
                                 log_error='chon_server not found')
        if not is_success:
            exit(0)
        is_success = self.loggin_tk()
        return is_success

    def find_slave_window(self, clear_all=False):
        self.close_all_login_page(clear_all=clear_all)
        path_image_live = 'image/login/live_image/find_slave_window.png'
        pt_windows = pywinauto.findwindows.find_windows(title_re=self.PT_NAME)
        is_success = False
        for pt_window in pt_windows:
            self.app = pywinauto.application.Application().connect(handle=pt_window)
            is_success = self.action(path_image_live, self.NAME_NV, 20, 10,
                                     log_error='slave_image not found', no_click=True)
            if is_success:
                break
        if not is_success:
            self.app = None
            print('aaaaaaaaaaaaaaa')
        return is_success

    def find_post_image(self, root_image_path, child_image_path):
        img_rgb = cv2.imread(root_image_path)
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        template = cv2.imread(child_image_path, 0)
        w, h = template.shape[::-1]

        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8
        loc = np.where(res >= threshold)
        # print((loc))
        # print(loc[0][0])
        # print(loc[1][0])
        for pt in zip(*loc[::-1]):
            return pt[0], pt[1]
        return None, None

    def exit_game_windown(self):
        self.app.kill()

    def close_all_login_page(self, clear_all=False):
        path_image_live = 'image/login/live_image/close_all_login_page.png'
        pt_windows = pywinauto.findwindows.find_windows(title_re=self.PT_NAME)
        for pt_window in pt_windows:
            self.app = pywinauto.application.Application().connect(handle=pt_window)
            is_login_page = self.action(
                path_image_live, 'image/login/login_dang_nhap_page.png', 20, 10, log_error='dang_nhap_page not found',
                no_click=True
            )
            if is_login_page or clear_all:
                self.exit_game_windown()

    def check_trang_bi_page(self, action=''):
        path_image_live = 'image/live_image/check_trang_bi_page.png'
        is_trang_bi_page = self.action(
            path_image_live, 'image/trang_bi.PNG', 20, 10, log_error='check_trang_bi_page not found',
            no_click=True
        )
        if action == 'CLOSE' and is_trang_bi_page:
            self.app.FSOnlineClass.type_keys('{F4}')
        elif action == 'OPEN' and not is_trang_bi_page:
            self.app.FSOnlineClass.type_keys('{F4}')
        return is_trang_bi_page


class Login(BaseAuto):
    def __init__(self, nv_info_key=''):
        super().__init__(nv_info_key)
        self.NV_INFO = NV_INFO[nv_info_key]
        self.NAME_NV = self.NV_INFO['NV_NAME']
        self.PASS = self.NV_INFO['PASS']
        self.TK = self.NV_INFO['TK']
        self.PT_PATH = self.NV_INFO['PT_PATH']
        self.PT_NAME = self.NV_INFO['PT_NAME']
        self.config_name = nv_info_key

    def loggin_tk(self):
        print(' loggin_tk ... ')
        path_image_live = 'image/login/live_image/login_page.png'
        skip_enter_server = self.action(path_image_live, 'image/login/login_vao_game_button.png', 20, 15,
                                        log_error='child_vao_game_button not found', no_click=True)
        if not skip_enter_server:
            if not self.login_button_action():
                return False
        else:
            print('Nhap pass luon')
            pass
        for elem in range(0, 100):

            path_image_live = 'image/login/live_image/login_page.png'
            is_success = self.action(path_image_live, 'image/login/login_vao_game_button.png', 20, 15,
                                     log_error='child_vao_game_button 2 not found', no_click=True)
            if is_success:
                break
            time.sleep(0.2)
            is_success = self.action(path_image_live, 'image/child_server_bao_tri.png', 20, 15,
                                     log_error='child_server_bao_tri not found', no_click=True)
            if is_success:
                time.sleep(0.2)
                self.app.FSOnlineClass.type_keys('{ENTER}')
                if not self.login_button_action():
                    return False
            time.sleep(0.2)

        for idx2 in range(0, 100):
            is_input_tk = self.nhap_tk()
            if not is_input_tk:
                self.exit_game_windown()
                is_success = self.init_game_windown()
                break
            if self.enter_game():
                break
            else:
                self.exit_game_windown()
                is_success = self.init_game_windown()
                break
        return is_success

    def enter_game(self):
        path_image_live = 'image/login/live_image/enter_game.png'
        for idx in range(20):
            time.sleep(0.5)
            is_success = self.action(path_image_live, 'image/{}/nv_name.png'.format(self.config_name), 20, 15,
                                     log_error='nv_name not found')
            if is_success:
                time.sleep(0.2)
                self.app.FSOnlineClass.type_keys('{ENTER}')
                is_success = self.check_login_success()
                break
        return is_success

    def check_login_success(self):
        path_image_live = 'image/login/live_image/check_login_success.png'
        for idx in range(20):
            time.sleep(0.5)
            is_success = self.action(path_image_live, 'image/{}/login_nv_name.PNG'.format(self.config_name), 20, 15,
                                     log_error='login_nv_name not found')
            if is_success:
                print('loggin thanh cong {}'.format(self.config_name))
                break
        return is_success

    def nhap_tk(self):
        path_image_live = 'image/login/live_image/nhap_tk.png'
        print('Nhap TK')

        is_success = self.action(path_image_live, 'image/login/login_input_tk.png', 20, 15,
                                 log_error='input_tk not found')
        if is_success:
            time.sleep(0.1)
            for idx in range(0, 30):
                self.app.FSOnlineClass.type_keys('{BACKSPACE}')
            time.sleep(0.1)
            self.app.FSOnlineClass.type_keys(self.TK)
            time.sleep(0.2)
            self.app.FSOnlineClass.type_keys('{TAB}')
            print('Nhap pass ')
            time.sleep(0.4)
            self.app.FSOnlineClass.type_keys(self.PASS)
            time.sleep(0.1)
            print('Nhap ENTER pass ')
            self.app.FSOnlineClass.type_keys('{ENTER}')
        return is_success

    def login_button_action(self):
        time.sleep(0.2)
        path_image_live = 'image/login/live_image/login_page.png'
        is_success = self.action(path_image_live, 'image/login/login_server_page.png', 20, 15,
                                 log_error='login_server_page not found', no_click=True)
        if not is_success:
            return False
        print(' Chuan bi login ')
        is_success = self.action(path_image_live, 'image/login/login_button.png', 20, 15,
                                 log_error='child_login_button not found')
        if not is_success:
            return False
        return True

    def login(self, clear_all=True):
        is_success = True
        if not self.find_slave_window(clear_all=clear_all):
            is_success = self.init_game_windown()
        self.app.FSOnlineClass.type_keys('{F7}')
        time.sleep(0.2)
        self.app.FSOnlineClass.type_keys('{F8}')
        print('login thanh cong')
        return is_success, self.app


class DNP(BaseAuto):
    def __init__(self, nv_info_key='', app=None):
        super().__init__(nv_info_key)
        self.NV_INFO = NV_INFO[nv_info_key]
        self.NAME_NV = self.NV_INFO['NV_NAME']
        self.PASS = self.NV_INFO['PASS']
        self.TK = self.NV_INFO['TK']
        self.PT_PATH = self.NV_INFO['PT_PATH']
        self.PT_NAME = self.NV_INFO['PT_NAME']
        self.config_name = nv_info_key
        self.pos = {
            'x': {
                'x_pos': 0,
                'y_pos': 0,
            },
            'y': {
                'x_pos': 0,
                'y_pos': 0,
            }
        }
        if app:
            self.app = app

    def by_dnp(self):
        self.app.FSOnlineClass.set_focus()
        print('Open ky tran cac ...')
        self.app.FSOnlineClass.type_keys('{F2}')
        time.sleep(0.2)
        if not self.ktc_check():
            return False
        else:
            if not self.ktc_by_dnp_item():
                return False
            self.app.FSOnlineClass.type_keys('{F2}')
            print('Close KTC')
            return True

    def ktc_check(self):
        print('Check KTC ....')
        self.app.FSOnlineClass.set_focus()
        time.sleep(0.2)
        path_image_live = 'image/by_dnp/live_image/ktc_check.png'
        self.take_screen_shot(path_image_live)
        time.sleep(0.1)
        x_pos, y_pos = self.find_post_image('image/by_dnp/dnp_ktc.png', path_image_live)
        # print()
        if x_pos is None:
            print('KTC not found aaaaaa')
            return False
        print('KTC was opening')
        return True

    def ktc_by_dnp_item(self):
        is_success = self.by_dnp_from_ktc()
        if is_success:
            return is_success
        print('By Di Nguyen Phu .....')
        path_image_live = 'image/by_dnp/live_image/ktc_by_dnp_item.png'
        is_success = self.action(path_image_live, 'image/by_dnp/dnp_truyen.png', 24, 15,
                                 log_error=' Truyen not found')
        if not is_success:
            return False

        path_image_live = 'image/by_dnp/live_image/ktc_dnp.png'
        is_success = self.action(path_image_live, 'image/by_dnp/dnp_end.png', 10, 5, log_error=' DNP page not found')
        if not is_success:
            return False
        time.sleep(0.5)
        is_success = self.by_dnp_from_ktc()
        return is_success

    def by_dnp_from_ktc(self):
        print('Mua DNP')
        path_image_live = 'image/by_dnp/live_image/by_dnp_from_ktc.png'
        is_success = self.action(path_image_live, 'image/by_dnp/dnp_ktc_dnp.png', 164, 51, log_error='DNP not found')
        if not is_success:
            return False
        time.sleep(0.4)
        path_image_live = 'image/by_dnp/live_image/by_dnp_from_ktc.png'
        is_success = self.action(path_image_live, 'image/by_dnp/dnp_confirm.png', 10, 5, log_error='Buy not found',
                                 debug=True)
        if not is_success:
            return False
        return True

    def open_dnp(self, check_only=False):
        print('Open hanh trang')
        if not self.check_trang_bi_page():
            self.app.FSOnlineClass.type_keys('{F4}')
        time.sleep(0.2)
        print('Open DNP')
        path_image_live = 'image/by_dnp/live_image/use_dnp.png'
        if check_only:
            is_success = self.action(
                path_image_live, 'image/by_dnp/dnp_dnp.png', 20, 15, log_error=' DNP not found in F4', no_click=True)
        else:
            is_success = self.action(
                path_image_live, 'image/by_dnp/dnp_dnp.png', 20, 15, log_error=' DNP not found in F4', right_click=True)

        return is_success

    def use_dnp(self, map_name, times_down):
        is_success = self.open_dnp()
        if not is_success:
            return False
        time.sleep(0.5)
        print('Go tk')
        path_image_live = 'image/by_dnp/live_image/use_dnp_tk.png'
        self.down_dnp(times_down)
        is_success = self.action(
            path_image_live, DNP_CFG[map_name]['dnp_name'], 20, 5, log_error=' Tay Ky not found in DNP')
        if not is_success:
            return False
        for idx in range(0, 100):
            path_image_live = 'image/by_dnp/live_image/use_dnp_tk.png'
            is_success = self.action(
                path_image_live, DNP_CFG[map_name]['dnp_confirm'], 20, 5, log_error='CHua toi {}'.format(map_name), no_click=True)
            if is_success:
                break
            time.sleep(0.2)
        time.sleep(1)
        self.exit_dnp_opening()
        if self.check_trang_bi_page():
            self.app.FSOnlineClass.type_keys('{F4}')
        self.app.FSOnlineClass.type_keys('{F7}')
        time.sleep(0.2)
        self.app.FSOnlineClass.type_keys('{F8}')
        return True

    def exit_dnp_opening(self):
        path_image_live = 'image/by_dnp/live_image/exit_dnp_opening.png'
        is_success = self.action(path_image_live, 'image/by_dnp/dnp_open.png', 20, 10,
                                 log_error='child_dnp_open not found')

        return is_success

    def go_to_map(self, map_name, npc_name='', times_down=0):
        is_success = self.open_dnp(check_only=True)
        if not is_success:
            is_success = self.by_dnp()
        if is_success:
            is_success = self.use_dnp(map_name=map_name, times_down=times_down)

        if is_success and npc_name != '':
            self.go_npc(npc_name)
        time.sleep(1)
        return is_success

    def down_dnp(self, times_down):
        path_image_live = 'image/by_dnp/live_image/down_dnp.png'
        for idx in range(times_down):
            is_success = self.action(
                path_image_live, 'image/by_dnp/down_dnp.PNG', 10, 10, log_error=' Not found down_dnp')

    def clean_post(self, pos_image='', adjust_x=0, adjust_y=0):
        path_image_live = 'image/by_dnp/live_image/input_post.png'
        is_success = self.action(path_image_live, pos_image, adjust_x, adjust_y, log_error=' Not found x_post')
        time.sleep(0.5)
        self.app.FSOnlineClass.type_keys('{END}')
        for idx in range(3):
            time.sleep(0.2)
            self.app.FSOnlineClass.type_keys('{BACKSPACE}')
        return is_success

    def input_post(self, x_pos, y_pos):
        self.clean_post('image/pos_clean_x.PNG', 50, 7)
        time.sleep(0.2)
        self.clean_post('image/pos_clean_y.PNG', -5, 4)
        path_image_live = 'image/by_dnp/live_image/input_post.png'
        is_success = self.action(path_image_live, 'image/x_pos.png', 18, 7, log_error=' Not found y_post')

        if not is_success:
            return is_success
        self.app.FSOnlineClass.type_keys(x_pos)

        path_image_live = 'image/live_image/tk.png'
        is_success = self.action(path_image_live, 'image/y_pos.png', 16, 4, log_error=' Not found y_post')

        if not is_success:
            return is_success
        self.app.FSOnlineClass.type_keys(y_pos)
        is_success = self.action(
            path_image_live, 'image/apply_pos.png', 18, 8, log_error=' Not found GO')

        return is_success

    def go_npc(self, npc_name):
        print('input pos ...')
        is_success = self.input_post(NPC_CFG[npc_name]['x_pos'], NPC_CFG[npc_name]['y_pos'])
        if not is_success:
            return is_success
        print('Dang di chuyen ...')
        time.sleep(3)

        print('Da Den')
        return is_success


class HBT(Login, DNP):
    def __init__(self, re_run='NNV', nv_info_key='chomchom'):
        super(HBT, self).__init__(nv_info_key=nv_info_key)
        self.skip_check_nnv_vo_cat_btn = False
        self.skip_check_nnv_xtt_btn = False
        self.skip_check_tnv_vo_cat_btn = False
        self.skip_check_tnv_xtt_btn = False
        self.re_run = re_run
        self.is_nnv_vl = False

    def nhan_nv_vi_lao_vo_cat(self):
        is_success = self.go_to_map('tay ky', 'vo cat')
        if not is_success:
            print("dung tai go_to_map('tay ky', 'vo cat')")
            return is_success
        is_success = self.nhan_nv_vi_lao(skip_check_vl_btn=self.skip_check_nnv_vo_cat_btn)
        if not is_success:
            print("dung tai nhan_nv_vi_lao")
            return is_success
        is_success = self.go_to_map('nhc', 'xich tinh tu', 1)
        if not is_success:
            print("dung tai go_to_map('nhc', 'xich tinh tu', 1)")
            return is_success

        is_success = self.nv_xich_tung_tu(skip_check_vl_btn=self.skip_check_nnv_xtt_btn, action='NNV')
        if not is_success or not self.is_nnv_vl:
            print("Nhan NV THAT BAI")
            return False
        return is_success

    def tnv_vi_lao(self):
        is_success = self.go_to_map('nhc', 'xich tinh tu', 2)
        if not is_success:
            print("dung tai go_to_map('nhc', 'xich tinh tu', 2)")
            return is_success
        is_success = self.nv_xich_tung_tu(skip_check_vl_btn=self.skip_check_tnv_xtt_btn, action='TNV')
        if not is_success:
            print("dung tai nv_xich_tung_tu tra nv")
            return is_success
        is_success = self.go_to_map('tay ky', 'vo cat')
        if not is_success:
            print("dung tai go_to_map('tay ky', 'vo cat')")
            return is_success
        is_success = self.tra_nv_vi_lao(skip_check_vl_btn=self.skip_check_tnv_vo_cat_btn)
        if not is_success:
            print("dung tai tra_nv_vi_lao")
            return is_success
        is_success = self.go_to_map('nhc', 'xich tinh tu', 2)
        if not is_success:
            print("dung tai self.go_to_map('nhc', 'xich tinh tu', 2)")
            return is_success
        return self.nv_xich_tung_tu()

    def set_skip_flag(self):
        self.skip_check_nnv_vo_cat_btn = False
        self.skip_check_nnv_xtt_btn = False
        self.skip_check_tnv_vo_cat_btn = False
        self.skip_check_tnv_xtt_btn = False
        self.is_nnv_vl = False
        if self.re_run == 'NNV':
            self.skip_check_nnv_vo_cat_btn = True
            self.skip_check_nnv_xtt_btn = True
        elif self.re_run == 'TNV':
            self.skip_check_tnv_vo_cat_btn = True
            self.skip_check_tnv_xtt_btn = True
        elif self.re_run == 'ALL':
            self.skip_check_nnv_vo_cat_btn = True
            self.skip_check_nnv_xtt_btn = True
            self.skip_check_tnv_vo_cat_btn = True
            self.skip_check_tnv_xtt_btn = True
        self.re_run = ''

    def run_make_hbt(self):
        if self.login(clear_all=False):
            for elem in range(27):
                self.set_skip_flag()
                print(' bat dau nhan nhiem vu')
                for idx in range(5):
                    is_success = self.nhan_nv_vi_lao_vo_cat()
                    if is_success:
                        break
                print(' bat dau danh boss')
                for idx in range(5):
                    is_success = self.danh_boss_vi_lao()
                    if is_success:
                        break
                if not is_success:
                    print("dung tai danh_boss_vi_lao")
                    return is_success
                print(' bat dau tra nhiem vu')
                for idx in range(5):
                    is_success = self.tnv_vi_lao()
                    if is_success:
                        break
            return is_success

    def danh_boss_vi_lao(self):
        is_success = self.go_to_map('tll', 'bdc', 20)
        if not is_success:
            return is_success
        is_success = self.bdc_go_to_boss()
        if not is_success:
            return is_success
        is_success = self.kill_boss()
        return is_success

    def end_doi_thoai(self, action=''):
        path_image_live = 'image/live_image/end_doi_thoai.png'
        for idx in range(10):
            is_success = self.action(
                path_image_live, 'image/doi_thoai.PNG', 5, 5, log_error=' Not found doi_thoai', no_click=True)
            if not is_success:
                print('ket thuc doi thoai')
                return True
            self.action(
                path_image_live, 'image/end_doi_thoai_btn.png', 5, 5, log_error=' Not found end_doi_thoai_btn')
            time.sleep(0.1)
            is_success = self.action(
                path_image_live, 'image/vi_lao/xac_nhan_vl.PNG', 5, 5, log_error=' Not found xac_nhan_vl')
            if action == 'NNV-XTT' and is_success:
                print('-----------------------------------')
                print(' Da nhan dc nhiem vu vi lao')
                print('-----------------------------------')
                self.is_nnv_vl = is_success
            time.sleep(0.1)
            self.app.FSOnlineClass.type_keys('{ENTER}')
        return False

    def tra_nv_vi_lao(self, skip_check_vl_btn=False):
        path_image_live = 'image/live_image/tra_nv_vi_lao.png'
        is_success = self.click_vo_cat()
        if not is_success:
            return is_success
        time.sleep(0.5)

        is_success = self.action(
            path_image_live, 'image/vi_lao/vi_lao_bt.PNG', 10, 10, log_error=' Not found vi_lao_bt')
        if not is_success and not skip_check_vl_btn:
            return is_success
        self.skip_check_tnv_vo_cat_btn = True
        is_success = self.end_doi_thoai()
        if not is_success:
            return is_success
        return is_success

    def kill_boss(self):
        path_image_live = 'image/live_image/kill_boss.png'
        is_success = self.mo_tdd()
        if not is_success:
            return is_success
        print('bat dau danh boss')
        for idx in range(7200):
            time.sleep(1)
            self.check_trang_bi_page(action='OPEN')
            time.sleep(0.5)
            is_success = self.action(
                path_image_live, 'image/vi_lao/vi_lao_clk.PNG', 5, 5, log_error=' Not found vi_lao_clk', no_click=True)
            time.sleep(0.2)
            if is_success:
                print('da time thay clk')
                break

        is_success = self.mo_tdd()
        return is_success

    def mo_tdd(self):
        path_image_live = 'image/live_image/mo_tdd.png'
        self.check_trang_bi_page(action='CLOSE')
        time.sleep(0.3)
        is_success = self.action(
            path_image_live, 'image/vi_lao/bat_ttd.PNG', 5, 5, log_error=' Not found bat_ttd')
        print('da bat tu dong danh')
        return is_success

    def click_vo_cat(self):
        path_image_live = 'image/live_image/click_vo_cat.png'
        for idx in range(10):
            is_success = self.action(
                path_image_live, 'image/by_dnp/npc/dnp_vo_cat.PNG', 5, 5, log_error=' Not found dnp_vo_cat')
            if is_success:
                break
            time.sleep(0.5)
            is_success = self.action(
                path_image_live, 'image/by_dnp/npc/dnp_vo_cat_2.PNG', 5, 5, log_error=' Not found dnp_vo_cat_2')
            if is_success:
                break
        return is_success

    def nhan_nv_vi_lao(self, skip_check_vl_btn=False):
        print('bat dau nhan nv vi lao')
        path_image_live = 'image/live_image/nhan_nv_vi_lao.png'
        time.sleep(0.5)
        is_success = self.click_vo_cat()
        if not is_success:
            return is_success
        time.sleep(0.5)
        is_success = self.action(
            path_image_live, 'image/vi_lao/vi_lao_bt.PNG', 10, 10, log_error=' Not found vi_lao_bt',
            debug=True)
        if not is_success and not skip_check_vl_btn:
            return is_success
        self.skip_check_nnv_vo_cat_btn = True
        time.sleep(0.5)
        is_success = self.end_doi_thoai()
        if not is_success:
            return is_success
        return is_success

    def gap_xtt(self):
        path_image_live = 'image/live_image/gap_xtt.png'
        for idx in range(5):
            is_success = self.action(
                path_image_live, 'image/vi_lao/xich_tinh_tu.PNG', 20, 10, log_error=' Not found xich_tinh_tu')
            if is_success:
                break
            time.sleep(0.2)
            is_success = self.action(
                path_image_live, 'image/vi_lao/xich_tung_tu_2.PNG', 20, 10, log_error=' Not found xich_tung_tu_2')
            if is_success:
                break
            time.sleep(0.2)
            is_success = self.action(
                path_image_live, 'image/vi_lao/xich_tinh_tu_3.PNG', 20, 10, log_error=' Not found xich_tinh_tu_3')
            if is_success:
                break
            time.sleep(0.2)
        return is_success

    def nv_xich_tung_tu(self, skip_check_vl_btn=False, action=''):
        path_image_live = 'image/live_image/nv_xich_tung_tu.png'
        time.sleep(0.5)
        is_success = self.gap_xtt()
        if not is_success:
            return is_success
        self.action(
            path_image_live, 'image/vi_lao/vi_lao_bt.PNG', 10, 10, log_error=' Not found vi_lao_bt')
        if not is_success and not skip_check_vl_btn:
            return is_success

        if action == 'NNV':
            self.skip_check_nnv_xtt_btn = True
        elif action == 'TNV':
            self.skip_check_tnv_xtt_btn = True

        is_success = self.end_doi_thoai(action + '-XTT')
        return is_success

    def bdc_go_to_boss(self):
        bdc_1_map = [
            {'step': 'image/vi_lao/bdc_t1_step_1.PNG', 'confirm': 'image/vi_lao/bdc_t1_step_1_confirm.PNG'},
            {'step': 'image/vi_lao/bdc_t1_step_2.PNG', 'confirm': 'image/vi_lao/bdc_t1_step_2_confirm.PNG'},
        ]
        bdc_2_map = [
            {'step': 'image/vi_lao/bdc_t2_step_1.PNG', 'confirm': 'image/vi_lao/bdc_t2_step_1_confirm.PNG'},
            {'step': 'image/vi_lao/bdc_t2_step_2.PNG', 'confirm': 'image/vi_lao/bdc_t2_step_2_confirm.PNG'},
            {'step': 'image/vi_lao/bdc_t2_step_3.PNG', 'confirm': 'image/vi_lao/bdc_t2_step_3_confirm.PNG'},
            {'step': 'image/vi_lao/bdc_t2_step_4.PNG', 'confirm': 'image/vi_lao/bdc_t2_step_4_confirm.PNG'},
            {'step': 'image/vi_lao/bdc_t2_step_5.PNG', 'confirm': 'image/vi_lao/bdc_t2_step_5_confirm.PNG'},
        ]
        for map in bdc_1_map:
            is_success = self.go_bdc(map['step'], map['confirm'])
            if not is_success:
                return is_success
        for map in bdc_2_map:
            adjust_x = 0
            adjust_y = 0
            if map['step'] == 'image/vi_lao/bdc_t2_step_5.PNG':
                adjust_x = 20
                adjust_y = 5

            is_success = self.go_bdc(map['step'], map['confirm'], adjust_x=adjust_x, adjust_y=adjust_y)
            if not is_success:
                return is_success
        return is_success

    def go_bdc(self, step, confirm, adjust_x=0, adjust_y=0):
        is_success = self.go_in_bdc(step, adjust_x=adjust_x, adjust_y=adjust_y)
        if not is_success:
            return is_success
        is_success = self.check_is_arrive(confirm)
        if not is_success:
            return is_success

        return is_success

    def check_is_arrive(self, image_name=''):
        path_image_live = 'image/live_image/check_is_arrive.png'
        for idx in range(100):
            time.sleep(0.5)
            is_success = self.action(
                path_image_live, image_name, 10, 10, log_error=' Not found {}'.format(image_name), no_click=True)
            if is_success:
                print('da toi ', image_name)
                break
        time.sleep(0.5)
        return is_success

    def go_in_bdc(self, image_name='', adjust_x=0, adjust_y=0):
        time.sleep(0.3)
        path_image_live = 'image/live_image/go_in_bdc.png'
        self.app.FSOnlineClass.type_keys('{TAB}')
        is_success = self.action(
            path_image_live, image_name, 10 + adjust_x, 10 + adjust_y, log_error=' Not found {}'.format(image_name))
        self.app.FSOnlineClass.type_keys('{TAB}')
        time.sleep(0.3)
        return is_success


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    get_hbt = HBT()
    get_hbt.run_make_hbt()
    # spam_ordinates()
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
