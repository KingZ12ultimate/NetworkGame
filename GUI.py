from direct.showbase.MessengerGlobal import messenger
from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectGui import *
from Globals import CHERRIES_TO_WIN


class GUIHandler:
    def __init__(self, backdrop, root_parent=None):
        if backdrop:
            self.backdrop = DirectFrame(frameColor=(0, 0, 0, 1),
                                        frameSize=(-1, 1, -1, 1),
                                        parent=root_parent)

    def destroy(self):
        if hasattr(self, "backdrop"):
            self.backdrop.destroy()


class MainMenu(GUIHandler):
    def __init__(self, button_images, click_sound, root_parent=None):
        GUIHandler.__init__(self, True, root_parent)
        self.main_menu = DirectFrame(frameColor=(1, 1, 1, 0))

        title = DirectLabel(text="Cherry Heist",
                                 scale=0.3,
                                 pos=(0, 0, 0.7),
                                 parent=self.main_menu,
                                 relief=None,
                                 text_fg=(1, 1, 1, 1))

        btn = DirectButton(text="Join Game",
                           command=messenger.send,
                           extraArgs=["join_game"],
                           pos=(0, 0, 0.2),
                           parent=self.main_menu,
                           scale=0.1,
                           clickSound=click_sound,
                           frameSize=(-4, 4, -1, 1),
                           frameTexture=button_images,
                           text_scale=0.75,
                           relief=DGG.GROOVE,
                           text_pos=(0, -0.2))
        btn.set_transparency(1)

        btn = DirectButton(text="Quit",
                           command=messenger.send,
                           extraArgs=["quit"],
                           pos=(0, 0, -0.2),
                           parent=self.main_menu,
                           scale=0.1,
                           clickSound=click_sound,
                           frameSize=(-4, 4, -1, 1),
                           frameTexture=button_images,
                           text_scale=0.75,
                           relief=DGG.GROOVE,
                           text_pos=(0, -0.2))
        btn.set_transparency(1)

    def destroy(self):
        self.main_menu.destroy()
        GUIHandler.destroy(self)


class LevelMenu(GUIHandler):
    def __init__(self, button_images, click_sound, root_parent=None):
        GUIHandler.__init__(self, True, root_parent)

        self.level_size_dialog = DirectDialog(frameSize=(-0.7, 0.7, -0.5, 0.5),
                                              command=self.dialog_button_command,
                                              extraArgs=["request_join"],
                                              fadeScreen=0.4,
                                              relief=DGG.FLAT,
                                              frameTexture="UI/stoneFrame.png",
                                              buttonTextList=["2", "3", "4"],
                                              buttonValueList=[2, 3, 4],
                                              buttonSize=(-0.2, 0.2, -0.1, 0.1),
                                              midPad=0.2)

        label = DirectLabel(text="Choose number of players",
                            parent=self.level_size_dialog,
                            scale=0.1,
                            pos=(0, 0, 0.2),
                            relief=None)

        for button in self.level_size_dialog.buttonList:
            button["frameTexture"] = button_images
            button["text_scale"] = 0.1
            button["clickSound"] = click_sound

    @staticmethod
    def dialog_button_command(button, event):
        messenger.send(event, [button])

    def destroy(self):
        self.level_size_dialog.destroy()
        GUIHandler.destroy(self)


class WaitingScreen(GUIHandler):
    def __init__(self, button_images, click_sound, max_players, root_parent=None):
        GUIHandler.__init__(self, True, root_parent)

        self.waiting_dialog = DirectDialog(frameSize=(-0.8, 0.8, -0.7, 0.7),
                                           fadeScreen=0.4,
                                           relief=DGG.FLAT,
                                           frameTexture="UI/stoneFrame.png")

        label = DirectLabel(text="Waiting for players...",
                            parent=self.waiting_dialog,
                            scale=0.15,
                            pos=(0, 0, 0.2),
                            relief=None)

        self.players_joined = 0
        self.max_players = max_players
        self.players_connected_label = DirectLabel(text="Players joined: {} / {}".format(self.players_joined, max_players),
                                                   parent=self.waiting_dialog,
                                                   scale=0.1,
                                                   pos=(0, 0, -0.05),
                                                   relief=None,
                                                   textMayChange=True)

        btn = DirectButton(text="Leave",
                           command=messenger.send,
                           extraArgs=["leave"],
                           pos=(0, 0, -0.3),
                           parent=self.waiting_dialog,
                           scale=0.1,
                           clickSound=click_sound,
                           frameSize=(-2, 2, -1, 1),
                           frameTexture=button_images,
                           text_scale=0.75,
                           relief=DGG.GROOVE,
                           text_pos=(0, -0.2))
        btn.set_transparency(1)

    def update_players_label(self, val):
        self.players_joined += val
        self.players_connected_label["text"] = "Players joined: {} / {}".format(self.players_joined, self.max_players)

    def destroy(self):
        self.waiting_dialog.destroy()
        GUIHandler.destroy(self)


class GameplayGUI(GUIHandler):
    def __init__(self, button_images, click_sound):
        GUIHandler.__init__(self, False)

        self.buttons = []

        btn = DirectButton(text="Pause",
                           command=messenger.send,
                           extraArgs=["pause"],
                           pos=(-0.25, 0, -0.4),
                           parent=base.a2dTopRight,
                           scale=0.1,
                           clickSound=click_sound,
                           frameSize=(-2, 2, -1, 1),
                           frameTexture=button_images,
                           text_scale=0.75,
                           relief=DGG.GROOVE,
                           text_pos=(0, -0.2))
        btn.set_transparency(1)
        self.buttons.append(btn)

        btn = DirectButton(text="Info",
                           command=messenger.send,
                           extraArgs=["info"],
                           pos=(-0.25, 0, -0.65),
                           parent=base.a2dTopRight,
                           scale=0.1,
                           clickSound=click_sound,
                           frameSize=(-2, 2, -1, 1),
                           frameTexture=button_images,
                           text_scale=0.75,
                           relief=DGG.GROOVE,
                           text_pos=(0, -0.2))
        btn.set_transparency(1)
        self.buttons.append(btn)

        self.info_menu = InfoMenu(button_images, click_sound)
        self.pause_menu = PauseMenu(button_images, click_sound)

    def destroy(self):
        self.info_menu.destroy()
        self.pause_menu.destroy()
        for button in self.buttons:
            button.destroy()


class InfoMenu:
    def __init__(self, button_images, click_sound):
        self.dialog = DirectDialog(frameSize=(-0.8, 0.8, -0.7, 0.7),
                                   fadeScreen=0.4,
                                   relief=DGG.FLAT,
                                   frameTexture="UI/stoneFrame.png")
        self.dialog.hide()

        title = DirectLabel(text="Instructions",
                            parent=self.dialog,
                            scale=0.15,
                            pos=(0, 0, 0.4),
                            relief=None)

        self.instructions = [
            self.add_instruction(0, "Use \"WASD\" keys to move"),
            self.add_instruction(0.1, "Use \"space\" key to jump"),
            self.add_instruction(0.2, "Use arrow keys to move the camera"),
            self.add_instruction(0.3, "Be the first to grab {} cherries!".format(CHERRIES_TO_WIN))
        ]

        btn = DirectButton(text="OK!",
                           command=messenger.send,
                           extraArgs=["resume", [self]],
                           pos=(0, 0, -0.4),
                           parent=self.dialog,
                           scale=0.1,
                           clickSound=click_sound,
                           frameSize=(-2, 2, -1, 1),
                           frameTexture=button_images,
                           text_scale=0.75,
                           relief=DGG.GROOVE,
                           text_pos=(0, -0.2))
        btn.set_transparency(1)

    def add_instruction(self, pos, msg):
        return DirectLabel(text=msg,
                           parent=self.dialog,
                           scale=0.08,
                           pos=(0, 0, 0.25 - pos),
                           relief=None)

    def destroy(self):
        self.dialog.destroy()


class PauseMenu:
    def __init__(self, button_images, click_sound):
        self.dialog = DirectDialog(frameSize=(-0.7, 0.7, -0.7, 0.7),
                                   fadeScreen=0.4,
                                   relief=DGG.FLAT,
                                   frameTexture="UI/stoneFrame.png")
        self.dialog.hide()

        label = DirectLabel(text="Game Paused",
                            parent=self.dialog,
                            scale=0.1,
                            pos=(0, 0, 0.2),
                            relief=None)

        btn = DirectButton(text="Resume",
                           command=messenger.send,
                           extraArgs=["resume", [self]],
                           pos=(0, 0, 0),
                           parent=self.dialog,
                           scale=0.1,
                           clickSound=click_sound,
                           frameSize=(-2, 2, -1, 1),
                           frameTexture=button_images,
                           text_scale=0.75,
                           relief=DGG.GROOVE,
                           text_pos=(0, -0.2))
        btn.set_transparency(1)

        btn = DirectButton(text="Leave",
                           command=messenger.send,
                           extraArgs=["leave"],
                           pos=(0, 0, -0.3),
                           parent=self.dialog,
                           scale=0.1,
                           clickSound=click_sound,
                           frameSize=(-2, 2, -1, 1),
                           frameTexture=button_images,
                           text_scale=0.75,
                           relief=DGG.GROOVE,
                           text_pos=(0, -0.2))
        btn.set_transparency(1)

    def destroy(self):
        self.dialog.destroy()


class GameOverMenu(GUIHandler):
    def __init__(self, button_images, click_sound):
        GUIHandler.__init__(self, False)

        self.game_over_dialog = DirectDialog(frameSize=(-1, 1, -1, 1),
                                             fadeScreen=0.7,
                                             relief=DGG.FLAT,
                                             frameTexture="UI/stoneFrame.png")

        self.label = DirectLabel(text="Game Over!",
                                 parent=self.game_over_dialog,
                                 scale=0.15,
                                 pos=(0, 0, 0.7),
                                 relief=None)

        label = DirectLabel(text="Final score:",
                                 parent=self.game_over_dialog,
                                 scale=0.12,
                                 pos=(0, 0, 0.55),
                                 relief=None)

        btn = DirectButton(text="Join New Game",
                           command=messenger.send,
                           extraArgs=["join_game"],
                           pos=(0, 0, -0.3),
                           parent=self.game_over_dialog,
                           scale=0.1,
                           clickSound=click_sound,
                           frameSize=(-4, 4, -1.25, 1.25),
                           frameTexture=button_images,
                           text_scale=0.75,
                           relief=DGG.GROOVE,
                           text_pos=(0, -0.2))
        btn.set_transparency(1)

        btn = DirectButton(text="Leave",
                           command=messenger.send,
                           extraArgs=["leave"],
                           pos=(0, 0, -0.6),
                           parent=self.game_over_dialog,
                           scale=0.1,
                           clickSound=click_sound,
                           frameSize=(-4, 4, -1.25, 1.25),
                           frameTexture=button_images,
                           text_scale=0.75,
                           relief=DGG.GROOVE,
                           text_pos=(0, -0.2))
        btn.set_transparency(1)

    def display_score(self, id_score_dict: dict[int, int], your_id):
        for i, _id in enumerate(id_score_dict):
            if _id == your_id:
                text = "{}) Player {} (You): {}".format(i + 1, _id, id_score_dict[_id])
                if i == 0:
                    self.label["text"] = "You Win!"
            else:
                text = "{}) Player {}: {}".format(i + 1, _id, id_score_dict[_id])
            DirectLabel(text=text,
                        parent=self.game_over_dialog,
                        scale=0.1,
                        pos=(0, 0, 0.4 - i * 0.15),
                        relief=None)

    def destroy(self):
        self.game_over_dialog.destroy()
