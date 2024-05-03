from direct.showbase.MessengerGlobal import messenger
from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectDialog import DirectDialog


class MainMenu:
    def __init__(self, root_parent=None):
        self.main_menu_backdrop = DirectFrame(frameColor=(0, 0, 0, 1),
                                              frameSize=(-1, 1, -1, 1),
                                              parent=root_parent)
        self.main_menu = DirectFrame(frameColor=(1, 1, 1, 0))
        self.title = DirectLabel(text="VIDEO GAMES",
                                 scale=0.3,
                                 pos=(0, 0, 0.7),
                                 parent=self.main_menu,
                                 relief=None,
                                 text_fg=(1, 1, 1, 1))

        button_images = (
            base.loader.load_texture("UI/UIButton.png"),
            base.loader.load_texture("UI/UIButtonPressed.png"),
            base.loader.load_texture("UI/UIButtonHighlighted.png"),
            base.loader.load_texture("UI/UIButtonDisabled.png")
        )

        self.level_size_dialog = DirectDialog(frameSize=(-0.7, 0.7, -0.5, 0.5),
                                              command=self.dialog_button_command,
                                              extraArgs=["join"],
                                              fadeScreen=0.4,
                                              relief=DGG.FLAT,
                                              frameTexture="UI/stoneFrame.png",
                                              buttonTextList=["2", "3", "4"],
                                              buttonValueList=[2, 3, 4],
                                              buttonSize=(-0.2, 0.2, -0.1, 0.1),
                                              midPad=0.2)
        self.level_size_dialog.hide()

        label = DirectLabel(text="Choose number of players",
                            parent=self.level_size_dialog,
                            scale=0.1,
                            pos=(0, 0, 0.2),
                            relief=None)

        for button in self.level_size_dialog.buttonList:
            button["frameTexture"] = button_images
            button["text_scale"] = 0.1

        btn = DirectButton(text="Join Game",
                           command=self.level_size_dialog.show,
                           pos=(0, 0, 0.2),
                           parent=self.main_menu,
                           scale=0.1,
                           frameSize=(-4, 4, -1, 1),
                           frameTexture=button_images,
                           text_scale=0.75,
                           relief=DGG.GROOVE,
                           text_pos=(0, -0.2))
        btn.set_transparency(1)

        self.waiting_dialog = DirectDialog(frameSize=(-0.7, 0.7, -0.7, 0.7),
                                           fadeScreen=0.4,
                                           relief=DGG.FLAT,
                                           frameTexture="UI/stoneFrame.png")
        self.waiting_dialog.hide()

        label = DirectLabel(text="Waiting for players...",
                            parent=self.waiting_dialog,
                            scale=0.1,
                            pos=(0, 0, 0.2),
                            relief=None)
        self.players_connected_label = DirectLabel(text="",
                                                   parent=self.waiting_dialog,
                                                   scale=0.1,
                                                   pos=(0, 0, 0),
                                                   relief=None)

        btn = DirectButton(text="Leave",
                           command=messenger.send,
                           extraArgs=["leave"],
                           pos=(0, 0, 0),
                           parent=self.waiting_dialog,
                           scale=0.1,
                           frameSize=(-2, 2, -1, 1),
                           frameTexture=button_images,
                           text_scale=0.75,
                           relief=DGG.GROOVE,
                           text_pos=(0, -0.2))
        btn.set_transparency(1)

    def dialog_button_command(self, button, event):
        self.level_size_dialog.hide()
        self.main_menu.hide()
        self.waiting_dialog.show()
        messenger.send(event, [button])
