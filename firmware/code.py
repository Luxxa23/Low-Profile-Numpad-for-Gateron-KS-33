print("Starting")

import board
import busio

from kmk.kmk_keyboard import KMKKeyboard
from kmk.keys import KC
from kmk.scanners import DiodeOrientation
from kmk.modules.layers import Layers
from kmk.modules.encoder import EncoderHandler
from kmk.extensions.media_keys import MediaKeys
from kmk.extensions.display import Display, SSD1306, TextEntry, ImageEntry
from kmk.extensions.display.ssd1306 import SSD1306
from kmk.extensions.lock_status import LockStatus
from kmk.modules.holdtap import HoldTap
from kmk.modules.macros import Macros, Press, Release, Tap, Delay


keyboard = KMKKeyboard()
layers = Layers()
holdtap = HoldTap()
encoder_handler = EncoderHandler()
macros = Macros()

keyboard.modules = [encoder_handler, holdtap, macros]
keyboard.extensions.append(MediaKeys())


keyboard.col_pins = (board.RX, board.SDA, board.A3, board.SCL)
keyboard.row_pins = (board.A2, board.SCK, board.MISO, board.MOSI, board.TX)
keyboard.diode_orientation = DiodeOrientation.COL2ROW


#GPIO Encoder
encoder_handler.pins = (board.A1, board.A0, None,),
encoder_handler.divisor = 4


i2c_bus = busio.I2C(board.SCL1, board.SDA1)

display_driver = SSD1306(
    i2c=i2c_bus,
#    device_address=0x3C,
)


#Layout to matrix:
#        Col0   Col1   Col2      Col3
#Row0    NUM     /       *       Top left (SW19)
#Row1    7       8       9       -
#Row2    4       5       6       +
#Row3    1       2       3
#Row4    0       ,       Enter   EncoderSW


CALC = KC.MACRO(
    Press(KC.LGUI),
    Tap(KC.R),
    Release(KC.LGUI),
    Delay(250),
    "calc.exe",
    Tap(KC.ENTER),
)
LAYER_TAP = KC.HT(CALC, KC.MO(4), prefer_hold=True, tap_interrupted=False, tap_time=250)


keyboard.keymap = [
    #base layer 0
    [
         KC.NUMLOCK, KC.KP_SLASH, KC.KP_ASTERISK, LAYER_TAP,
         KC.KP_7, KC.KP_8, KC.KP_9, KC.KP_MINUS,
         KC.KP_4, KC.KP_5, KC.KP_6, KC.KP_PLUS,
         KC.KP_1, KC.KP_2, KC.KP_3, KC.B,
         KC.KP_0, KC.KP_DOT, KC.KP_ENTER, KC.MEDIA_PLAY_PAUSE,
    ],
    #caps layer 1
    [
         KC.NUMLOCK, KC.KP_SLASH, KC.KP_ASTERISK, LAYER_TAP,
         KC.KP_7, KC.KP_8, KC.KP_9, KC.KP_MINUS,
         KC.KP_4, KC.KP_5, KC.KP_6, KC.KP_PLUS,
         KC.KP_1, KC.KP_2, KC.KP_3, KC.B,
         KC.KP_0, KC.KP_DOT, KC.KP_ENTER, KC.MEDIA_PLAY_PAUSE,
    ],
    #num layer 2
    [
         KC.NUMLOCK, KC.KP_SLASH, KC.KP_ASTERISK, LAYER_TAP,
         KC.KP_7, KC.KP_8, KC.KP_9, KC.KP_MINUS,
         KC.KP_4, KC.KP_5, KC.KP_6, KC.KP_PLUS,
         KC.KP_1, KC.KP_2, KC.KP_3, KC.B,
         KC.KP_0, KC.KP_DOT, KC.KP_ENTER, KC.MEDIA_PLAY_PAUSE,
    ],
    #num+caps layer 3
    [
         KC.NUMLOCK, KC.KP_SLASH, KC.KP_ASTERISK, LAYER_TAP,
         KC.KP_7, KC.KP_8, KC.KP_9, KC.KP_MINUS,
         KC.KP_4, KC.KP_5, KC.KP_6, KC.KP_PLUS,
         KC.KP_1, KC.KP_2, KC.KP_3, KC.B,
         KC.KP_0, KC.KP_DOT, KC.KP_ENTER, KC.MEDIA_PLAY_PAUSE,
    ],
    # vol knob layer 4
    [
         KC.NUMLOCK, KC.KP_SLASH, KC.KP_ASTERISK, KC.TRNS,
         KC.KP_7, KC.KP_8, KC.KP_9, KC.KP_MINUS,
         KC.KP_4, KC.KP_5, KC.KP_6, KC.KP_PLUS,
         KC.KP_1, KC.KP_2, KC.KP_3, KC.B,
         KC.KP_0, KC.KP_DOT, KC.KP_ENTER, KC.MUTE,
    ],
]


encoder_handler.map = [ ((KC.MEDIA_PREV_TRACK, KC.MEDIA_NEXT_TRACK),), #layer 0
                        ((KC.MEDIA_PREV_TRACK, KC.MEDIA_NEXT_TRACK),), #layer 1
                        ((KC.MEDIA_PREV_TRACK, KC.MEDIA_NEXT_TRACK),), #layer 2
                        ((KC.MEDIA_PREV_TRACK, KC.MEDIA_NEXT_TRACK),), #layer 3
                        ((KC.AUDIO_VOL_DOWN, KC.AUDIO_VOL_UP),), #layer 4
                      ]


display = Display(
    display=display_driver,
    height=32,
    dim_time=10,
    dim_target=0.1,
    off_time=1800,
    brightness=1,
)


class OLEDLockStatus(LockStatus):

    def set_lock_oled(self):
        if self.get_caps_lock() and self.get_num_lock() == False:
            keyboard.tap_key(KC.DF(1))
        elif self.get_num_lock() and self.get_caps_lock() == False:
            keyboard.tap_key(KC.DF(2))
        elif self.get_num_lock() and self.get_caps_lock():
            keyboard.tap_key(KC.DF(3))
        elif self.get_num_lock() == False and self.get_caps_lock() == False:
            keyboard.tap_key(KC.DF(0))

    def after_hid_send(self, sandbox):
        super().after_hid_send(sandbox)  # Critically important. Do not forget
        if self.report_updated:
            self.set_lock_oled()


display.entries = [
    ImageEntry(image="None.bmp", x=0, y=0, layer=0),
    ImageEntry(image="C.bmp", x=0, y=0, layer=1),
    ImageEntry(image="N.bmp", x=0, y=0, layer=2),
    ImageEntry(image="CN.bmp", x=0, y=0, layer=3),
    ImageEntry(image="Vol.bmp", x=0, y= 0, layer= 4),
]


keyboard.extensions.append(display)
keyboard.extensions.append(OLEDLockStatus())
keyboard.extensions.append(Layers)

if __name__ == '__main__':
    keyboard.go()
