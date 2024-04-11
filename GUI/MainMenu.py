from direct.showbase.MessengerGlobal import messenger
from direct.gui import DirectGuiGlobals as DGG

from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectButton import DirectButton


class MainMenu:
    def __init__(self, root_parent=None):
        self.main_menu_backdrop = DirectFrame(frameColor=(0, 0, 0, 1),
                                              frameSize=(-1, 1, -1, 1),
                                              parent=root_parent)
        self.main_menu = DirectFrame(frameColor=(1, 1, 1, 0))
        self.title1 = DirectLabel(text="VIDEO GAMES",
                                  scale=0.3,
                                  pos=(0, 0, 0.7),
                                  parent=self.main_menu,
                                  relief=None,
                                  text_fg=(1, 1, 1, 1))

        self.btn = DirectButton(text="Join Game",
                                command=messenger.send,
                                extraArgs=["join"],
                                pos=(0, 0, 0.2),
                                parent=self.main_menu,
                                scale=0.1,
                                frameSize=(-4, 4, -1, 1),
                                text_scale=0.75,
                                relief=DGG.FLAT,
                                text_pos=(0, -0.2))
        self.btn.set_transparency(1)
