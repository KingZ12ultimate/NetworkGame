import simplepbr

from direct.showbase.ShowBase import ShowBase
from direct.fsm.FSM import FSM
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import TextNode, WindowProperties, DirectionalLight, AmbientLight
from Repositories.ClientRepository import GameClientRepository
from Camera import Camera
from GUI import *


class GameClient(ShowBase, FSM):
    def __init__(self):
        ShowBase.__init__(self)
        FSM.__init__(self, "Client")

        properties = WindowProperties()
        properties.set_size(1280, 720)
        properties.set_title("Game")
        self.win.request_properties(properties)

        self.disable_mouse()
        self.set_background_color(0.745, 0.894, 1, 1)

        # region Lighting Setup
        pipeline = simplepbr.init()
        pipeline.use_normal_maps = True

        a_light = AmbientLight('a_light')
        a_light.set_color((0.2, 0.2, 0.2, 1))
        alnp = self.render.attach_new_node(a_light)
        self.render.set_light(alnp)

        d_light = DirectionalLight('d_light')
        d_light.set_color_temperature(65000)
        dlnp = self.render.attach_new_node(d_light)
        dlnp.node().set_shadow_caster(True)
        dlnp.set_p(-50)
        self.render.set_light(dlnp)
        # endregion

        self.update_task = None
        self.camera_mgr: Camera | None = None

        self.cr = None
        self.can_start_client = False
        self.current_menu = None
        self.current_menu_events = {}
        self.score_text = {}
        self.id_score_dict = {}
        self.exitFunc = self.clean_exit

        self.button_images = (
            self.loader.load_texture("UI/UIButton.png"),
            self.loader.load_texture("UI/UIButtonPressed.png"),
            self.loader.load_texture("UI/UIButtonHighlighted.png"),
            self.loader.load_texture("UI/UIButtonDisabled.png")
        )

        self.status_title = OnscreenText(text="", pos=(-0.1, 0.12), scale=0.08,
                                         parent=self.a2dBottomRight, align=TextNode.ARight,
                                         fg=(1, 1, 1, 1), shadow=(0, 0, 0, 1))
        self.status_title.hide()
        self.accept("update_status_title", self.update_status_title)

        # region Sound
        self.mute = False

        self.menu_music = self.loader.load_music("Assets/Sounds/menu_music.mp3")
        self.menu_music.set_loop(True)
        self.menu_music.set_volume(0.4)
        self.gameplay_music = self.loader.load_music("Assets/Sounds/gameplay_music.mp3")
        self.gameplay_music.set_loop(True)
        self.current_music = None
        self.menu_music_volume = 0.1
        self.regular_music_volume = 0.4
        self.music_volume = self.regular_music_volume  # holds the music volume before it was muted
        self.current_music_volume = lambda: 0.0 if self.mute else self.music_volume

        click_sound = self.loader.load_sfx("Assets/Sounds/UI_click.ogg")
        item_pickup_sound = self.loader.load_sfx("Assets/Sounds/item_pickup.mp3")
        running_sound = self.loader.load_sfx("Assets/Sounds/running_sound.mp3")
        running_sound.set_loop(True)

        self.sounds = {
            "click": click_sound,
            "pickup": item_pickup_sound,
            "run": running_sound
        }

        self.mute_btn = DirectButton(text="Mute",
                                     command=messenger.send,
                                     extraArgs=["mute"],
                                     pos=(-0.25, 0, -0.15),
                                     parent=self.a2dTopRight,
                                     scale=0.1,
                                     clickSound=click_sound,
                                     frameSize=(-2, 2, -1, 1),
                                     frameTexture=self.button_images,
                                     text_scale=0.75,
                                     relief=DGG.GROOVE,
                                     text_pos=(0, -0.2))
        self.mute_btn.set_transparency(1)
        self.accept("mute", self.toggle_audio)
        # endregion

        self.request("MainMenu")

    # region Finite State Machine
    def enterMainMenu(self):
        if self.menu_music.status() is self.menu_music.READY:
            self.current_music = self.menu_music
            self.music_volume = self.regular_music_volume
            self.menu_music.set_volume(self.current_music_volume())
            self.menu_music.play()

        self.cleanup_client()
        self.current_menu = MainMenu(self.button_images, self.sounds["click"], self.render2d)

        self.current_menu_events = {
            "join_game": self.setup_client,
            "quit": self.userExit
        }
        self.accept_dict(self.current_menu_events)

    def defaultExit(self):
        if self.current_menu is not None:
            self.current_menu.destroy()
            del self.current_menu
            self.ignore_dict(self.current_menu_events)
        FSM.defaultExit(self)

    def enterLevelMenu(self):
        if self.menu_music.status() is self.menu_music.READY:
            self.current_music = self.menu_music
            self.menu_music.set_volume(self.current_music_volume())
            self.menu_music.play()

        self.current_menu = LevelMenu(self.button_images, self.sounds["click"], self.render2d)
        self.current_menu_events = {
            "request_join": self.join
        }
        self.accept_dict(self.current_menu_events)

    def enterWaiting(self, max_players):
        self.current_menu = WaitingScreen(self.button_images, self.sounds["click"], max_players, self.render2d)
        self.current_menu_events = {
            "player_joined": [self.current_menu.update_players_label, [1]],
            "player_left": [self.current_menu.update_players_label, [-1]],
            "start_level": [self.request, ["Playing"]],
            "leave": self.clean_exit
        }
        self.accept_dict(self.current_menu_events)

    def enterPlaying(self, player_ids=None):
        if player_ids is None:
            player_ids = []
        if self.menu_music.status() is self.menu_music.PLAYING:
            self.menu_music.stop()
        self.gameplay_music.set_volume(self.current_music_volume())
        if self.gameplay_music.status() is self.gameplay_music.READY:
            self.current_music = self.gameplay_music
            self.gameplay_music.play()

        self.current_menu = GameplayGUI(self.button_images, self.sounds["click"])
        self.current_menu.info_menu.dialog.show()
        self.start_level(player_ids)

        def show_menu(menu):
            self.music_volume = self.menu_music_volume
            self.gameplay_music.set_volume(self.current_music_volume())
            menu.dialog.show()

        def hide_menu(menu):
            self.music_volume = self.regular_music_volume
            self.gameplay_music.set_volume(self.current_music_volume())
            menu.dialog.hide()

        self.current_menu_events = {
            "end_level": [self.request, ["GameOver"]],
            "info": [show_menu, [self.current_menu.info_menu]],
            "pause": [show_menu, [self.current_menu.pause_menu]],
            "resume": hide_menu,
            "leave": self.leave,
            "play_sound": self.play_sound,
            "stop_sound": self.stop_sound
        }
        self.accept_dict(self.current_menu_events)

    def enterGameOver(self):
        self.music_volume = self.menu_music_volume
        self.gameplay_music.set_volume(self.current_music_volume())
        self.end_level()

        def join_new_game():
            self.cr.request_leave()
            self.request("LevelMenu")

        self.current_menu = GameOverMenu(self.button_images, self.sounds["click"])
        self.current_menu_events = {
            "join_game": join_new_game,
            "leave": self.clean_exit
        }
        self.accept_dict(self.current_menu_events)

        # Display the ranking of the players by their scores
        self.id_score_dict = dict(sorted(self.id_score_dict.items(), key=lambda x: x[1], reverse=True))
        self.current_menu.display_score(self.id_score_dict, self.cr.local_player_id)

    def exitGameOver(self):
        for _id in self.id_score_dict.copy():
            del self.id_score_dict[_id]

        self.current_menu.destroy()
        del self.current_menu
        self.ignore_dict(self.current_menu_events)

        self.music_volume = self.regular_music_volume
        self.gameplay_music.stop()
    # endregion

    # region Client / Server
    def setup_client(self):
        if not self.can_start_client:
            self.request("MainMenu")
            return

        self.ignore("join_game")
        self.cr = GameClientRepository(
            self.request, "LevelMenu", self.request, "MainMenu")

    def cleanup_client(self):
        self.can_start_client = False
        if not self.cr:
            self.can_start_client = True
            return

        for obj in self.cr.doId2do.values():
            obj.sendDeleteMsg()

        for do_id in self.cr.doId2do.copy().keys():
            self.cr.deleteObject(do_id)

        self.cr.sendDisconnect()
        del self.cr
        self.cr = None
        self.can_start_client = True

    def join(self, max_players):
        self.request("Waiting", max_players)
        self.cr.request_join(max_players)

    def leave(self):
        """ Leave the current level. """
        if self.gameplay_music.status() is self.gameplay_music.PLAYING:
            self.gameplay_music.stop()
        self.end_level()
        self.clean_exit()

    def clean_exit(self):
        if self.cr is not None:
            self.cr.request_leave()
            self.request("MainMenu")
    # endregion

    # region Level Related Methods
    def start_level(self, player_ids):
        player = self.cr.doId2do[self.cr.local_player_id]

        self.camera_mgr = Camera(self.camera, player, 60, 10, 0.75)
        player.set_input_space(self.camera)
        self.update_task = self.task_mgr.add(self.update, "update-task")

        for i, _id in enumerate(player_ids):
            self.id_score_dict[_id] = 0
            if _id == self.cr.local_player_id:
                text = "Player {} (You): {}".format(_id, 0)
            else:
                text = "Player {}: {}".format(_id, 0)
            self.score_text[_id] = OnscreenText(text=text,
                                                parent=self.a2dTopLeft,
                                                pos=(0, -0.08 - i * 0.1),
                                                scale=0.1,
                                                align=TextNode.ALeft,
                                                mayChange=True)

        self.accept("update_score", self.update_score)

    def end_level(self):
        self.update_task.remove()
        self.camera_mgr = None

        for sound in self.sounds.values():
            sound.stop()

        for _id in self.score_text.copy():
            self.score_text[_id].destroy()
            del self.score_text[_id]

    def update_score(self, player_id, value):
        self.id_score_dict[player_id] = value
        if player_id == self.cr.local_player_id:
            text = "Player {} (You): {}".format(player_id, value)
        else:
            text = "Player {}: {}".format(player_id, value)
        self.score_text[player_id]["text"] = text

    def update(self, task):
        """The main task that will handle the client-side game logic"""
        dt = self.clock.get_dt()
        self.cr.update()
        self.camera_mgr.update(dt)
        return task.cont
    # endregion

    # region Helper Functions
    def accept_dict(self, event_dict):
        """Helper function to accept a dictionary of events.
        Key: event name
        Value: function or list [function, extra args]"""
        for event, func in event_dict.items():
            if type(func) is list:
                self.accept(event, func[0], func[1])
            else:
                self.accept(event, func)

    def ignore_dict(self, event_dict):
        """Ignores a set of events."""
        for event in event_dict.keys():
            self.ignore(event)

    def play_sound(self, name):
        if name not in self.sounds:
            print("Can't play sound: sound name doesn't exist.")
            return
        self.sounds[name].play()

    def stop_sound(self, name):
        sound = self.sounds[name]
        if sound.status() is sound.PLAYING:
            sound.stop()

    def toggle_audio(self):
        if self.mute:
            self.mute = not self.mute
            self.mute_btn["text"] = "Mute"
            self.current_music.set_volume(self.current_music_volume())
            for sound in self.sounds.values():
                sound.set_volume(1.0)
        else:
            self.mute = not self.mute
            self.mute_btn["text"] = "Unmute"
            self.current_music.set_volume(0.0)
            for sound in self.sounds.values():
                sound.set_volume(0.0)

    def update_status_title(self, text):
        self.status_title["text"] = text
        self.status_title.show()

        def hide_title(task):
            self.status_title.hide()
        self.task_mgr.do_method_later(3.0, hide_title, "hide_title")
    # endregion


client = GameClient()
client.run()
