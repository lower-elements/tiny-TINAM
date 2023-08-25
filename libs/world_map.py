import contextlib
from . import audio, consts, options
from .objects import entity


class Map:
    def __init__(self, game, minx=0, miny=0, minz=0, maxx=0, maxy=0, maxz=0):
        """Constructs a basic map:
        params:
        minx (int): Minimum x of the map
        miny (int): Minimum y of the map
        minz (int): Minimum Z of the map
        maxx (int): Maximum x of the map
        maxy (int): Maximum y of the map
        maxz (int): Maximum z of the map"""
        self.game = game
        self.minx, self.miny, self.minz = minx, miny, minz
        self.maxx = maxx
        self.maxy = maxy
        self.maxz = maxz
        # Store our tiles
        self.tile_list = []
        self.door_list=[]
        # Store our zones
        self.zone_list = []
        # ambience list
        self.ambience_list = []
        self.music_list=[]
        self.reverb_list = []
        self.entities = {}

    def in_bound(self, x, y, z):
        """verifies whether the hole map covers a certain coordinate
        params:
        x (int) the x of the coordinate
        y (int) the y of the coordinate
        z (int) the z of the coordinate
        returns:
        (bool) true if the objects covers this coordinate, or false if otherwise
        """
        x = int(x)
        y = int(y)
        z = int(z)
        return (
            x >= self.minx
            and x <= self.maxx
            and y >= self.miny
            and y <= self.maxy
            and z >= self.minz
            and z <= self.maxz
        )

    def loop(self):
        for i in self.entities.values():
            i.loop()

    def destroy(self, destroy_entities=True):
        audio.set_global_reverb(None)
        for i in self.reverb_list.copy():
            i.destroy()
        if destroy_entities:
            for i in self.entities.values():
                i.destroy()
            self.entities.clear()
        self.reverb_list.clear()
        self.tile_list.clear()
        self.zone_list.clear()
        self.door_list.clear()
        for i in self.ambience_list.copy():
            i.leave(destroy=True)
        self.ambience_list.clear()
        for i in self.music_list.copy():
            i.leave(destroy=True)
        self.music_list.clear()

    def get_ambiences_at(self, x, y, z):
        for i in self.ambience_list:
            if i.in_bound(x, y, z):
                yield i

    def get_musics_at(self, x, y, z):
        for i in self.music_list:
            if i.in_bound(x, y, z):
                yield i

    def get_tile_at(self, x, y, z):
        """Returns a tile at a specified coordinates
        params:
        x (int): The x coordinate from which a tile will be retrieved
        y (int): The y coordinate from which a tile will be retrieved
        z (int): The z coordinate from which a tile will be retrieved
        Return Value:
        A blank string if a tile wasn't found or a tiletype which is within the x, y, and z coordinate"""
        found_responses = ""
        for i in self.tile_list:
            if i.in_bound(x, y, z):
                found_responses = i.tiletype
        return found_responses

    def get_door_at(self, x, y, z):
        """Returns a door at a specified coordinates
        params:
        x (int): The x coordinate from which a door will be retrieved
        y (int): The y coordinate from which a door will be retrieved
        z (int): The z coordinate from which a door will be retrieved
        Return Value:
        Noneif a door wasn't found or a door object  which is within the x, y, and z coordinate"""
        return next((i for i in self.door_list if i.at_bound(x, y, z)), None)

    def get_zone_at(self, x, y, z):
        """Same as get_tile_at, except deals with zones"""
        found_responses = ""
        for i in self.zone_list:
            if i.in_bound(x, y, z):
                found_responses = i.zonename
        return found_responses

    def spawn_reverb(self, minx, maxx, miny, maxy, minz, maxz, t60, damp = 1500):
        #self.reverb_list.append(Reverb(minx, maxx, miny, maxy, minz, maxz, t60, damp))
        pass

    def get_reverb_at(self, x, y, z):
        for i in self.reverb_list:
            if i.in_bound(x, y, z):
                return i

    def spawn_music(self, minx, maxx, miny, maxy, minz, maxz, sound):
        with contextlib.suppress(Exception):
            self.music_list.append(
                Ambience(minx, maxx, miny, maxy, minz, maxz, sound, options.get("music_volume", 25))
            )


    def spawn_ambience(self, minx, maxx, miny, maxy, minz, maxz, sound, volume=100):
        with contextlib.suppress(Exception):
            self.ambience_list.append(
                Ambience(minx, maxx, miny, maxy, minz, maxz, sound, volume)
            )

    def spawn_zone(self, minx=0, maxx=0, miny=0, maxy=0, minz=0, maxz=0, type=""):
        """Spawns a zone
        Params:
        minx (int): The minimum x of the zone
        maxx (int): The maximum x of the zone
        miny (int): The minimum y of the zone
        maxy (int): The maximum y of the zone
        minz (int): The minimum z of the zone
        maxz (int): The maximum z of the zone"""
        self.zone_list.append(Zone(minx, maxx, miny, maxy, minz, maxz, type))


    def spawn_platform(self, minx=0, maxx=0, miny=0, maxy=0, minz=0, maxz=0, type=""):
        """Spawns a platform
        Params:
        minx (int): The minimum x of the tile
        maxx (int): The maximum x of the tile
        miny (int): The minimum y of the tile
        maxy (int): The maximum y of the tile
        minz (int): The minimum z of the tile
        maxz (int): The maximum z of the tile"""
        self.tile_list.append(Tile(minx, maxx, miny, maxy, minz, maxz, type))

    def spawn_door(self, minx=0, maxx=0, miny=0, maxy=0, minz=0, maxz=0, walltype="", tiletype=""):
        """Spawns a door
        Params:
        minx (int): The minimum x of the tile
        maxx (int): The maximum x of the tile
        miny (int): The minimum y of the tile
        maxy (int): The maximum y of the tile
        minz (int): The minimum z of the tile
        maxz (int): The maximum z of the tile
        walltype (str) the type of the wall when the door is closed
        tiletype (str) the tile of of the door when it is open
        """
        self.door_list.append(Door(minx, maxx, miny, maxy, minz, maxz, walltype, tiletype, self))

    def get_min_x(self):
        """Returns the minimum x"""
        return self.minx

    def get_min_y(self):
        """Returns the minimum y"""
        return self.miny

    def get_min_z(self):
        """Returns the minimum z"""
        return self.minz

    def get_max_x(self):
        """Returns the maximum x"""
        return self.maxx

    def get_max_y(self):
        """Returns the maximum y"""
        return self.maxy

    def get_max_z(self):
        """Returns the maximum z"""
        return self.maxz

    def spawn_entity(self, name, x, y, z, hp=100):
        if self.entities.get(name):
            self.entities[name].destroy()
        self.entities[name] = entity.Entity(self.game, self, x, y, z, hp)
        return self.entities[name]

    def get_entities_at(self, x, y, z):
        for i in self.entities.values():
            if i.x == x and i.y == y and i.z == z:
                yield i

    def remove_entity(self, name):
        if entity := self.entities.get(name):
            entity.destroy()
            del self.entities[name]


class BaseMapObj:
    """base map object
    this object is the base class from where tiles, zones and custom map objects inherit
    """

    def __init__(self, minx, maxx, miny, maxy, minz, maxz, type):
        """the BaseMapObj constructor
        params:
        minx (int) the minimum x, from where  the object starts
        maxx (int) the maximum x of the map
        miny (int) the minimum y of the map
        maxy (int) the maximum y of the map
        minz (int) the minimum z of the map
        maxz (int) the maximum z of the map
        type (str) the type of the map object, tile, zone, or whatever
        """
        self.minx = minx
        self.maxx = maxx
        self.miny = miny
        self.maxy = maxy
        self.minz = minz
        self.maxz = maxz
        self.type = type

    def in_bound(self, x, y, z):
        """verifies whether the current object covers a certain coordinate
        params:
        x (int) the x of the coordinate
        y (int) the y of the coordinate
        z (int) the z of the coordinate
        returns:
        (bool) true if the objects covers this coordinate, or false if otherwise
        """
        x = int(x)
        y = int(y)
        z = int(z)
        return (
            x >= self.minx
            and x <= self.maxx
            and y >= self.miny
            and y <= self.maxy
            and z >= self.minz
            and z <= self.maxz
        )


class Reverb(BaseMapObj):
    def __init__(self, minx, maxx, miny, maxy, minz, maxz, t60, damp=1500):
        super().__init__(minx, maxx, miny, maxy, minz, maxz, "reverb")
        self.t60 = t60
        self.damp = damp
        self.reverb = audio.reverb(t60, damp) if t60 else None

    def destroy(self):
        with contextlib.suppress(Exception):
            # in case its already destroyed
            if self.reverb:
                self.reverb.delete()
                self.reverb.delete_effect()

class Ambience(BaseMapObj):
    def __init__(self, minx, maxx, miny, maxy, minz, maxz, sound, volume=100):
        super().__init__(minx, maxx, miny, maxy, minz, maxz, "ambience")
        self.file = sound
        self.volume = volume
        self.fade_time = 0.5
        self.sound = audio.play_direct(
            self.file, True, 0, options.get("stream_ambience", True)
        )
        self.playing = False

    def enter(self):
        if not self.playing:
            self.playing = True
            #self.sound.fade(_from=self.volume / 3, to=self.volume, fade_time=self.fade_time * 2)
            if self.sound: self.sound.set_volume(self.volume)

    def leave(self, destroy=False):
        evt = consts.EVT_DESTROY if destroy else 0
        if self.playing:
            self.playing = False
            #self.sound.fade(to=0, fade_time=self.fade_time, evt=evt)
            if self.sound: 
                self.sound.set_volume(0)
        if self.sound and destroy: self.sound.destroy()

class Tile(BaseMapObj):
    """An internal tile class. You do not need to create any objects with this type externally"""

    def __init__(self, minx, maxx, miny, maxy, minz, maxz, type):
        super(Tile, self).__init__(minx, maxx, miny, maxy, minz, maxz, "tile")
        self.tiletype = type


class Door(BaseMapObj):
    def __init__(self, minx, maxx, miny, maxy, minz, maxz, closetype, opentype, map):
        super().__init__(minx, maxx, miny, maxy, minz, maxz, closetype)
        self.closetile=Tile(minx, maxx, miny, maxy, minz, maxz, closetype)
        self.opentilebase=Tile(minx, maxx, miny, maxy, minz, minz, opentype)
        self.opentile_air=Tile(minx, maxx, miny, maxy, minz+1, maxz, "air") if self.maxz>self.minz else None
        self.map=map
        self.map.tile_list.append(self.closetile)
        self.tile_index=len(self.map.tile_list)-1
        self.air_index=None
        self.open = False
        self.src=audio.Src()
    def switch_state(self, locked=False, to_open=True, silent=False):
        if to_open and not locked:
            self.open = True
            self.src.move(self.minx, self.maxy, self.minz)
            if not silent: self.src.play_sound(
                "door/open",
                False,
                100
            )
            self.map.tile_list.pop(self.tile_index)
            self.map.tile_list.append(self.opentilebase)
            self.tile_index=len(self.map.tile_list)-1
            if self.opentile_air: 
                self.map.tile_list.append(self.opentile_air)
                self.air_index=len(self.map.tile_list)-1
        elif not to_open:
            self.open = False
            if self.opentile_air:
                if self.air_index: self.map.tile_list.pop(self.air_index)
                self.air_index=None
            self.map.tile_list.pop(self.tile_index)
            self.map.tile_list.append(self.closetile)
            self.tile_index=len(self.map.tile_list)-1
        else:
            self.src.move(self.maxx, self.miny+(self.maxy-self.miny), self.minz)
            self.src.play_sound(
                "door/locked",
                False,
                100
            )


    def at_bound(self, x, y, z):
        """returns wheather you are in any valid locations to open a door
        params:
        x (int) the x of the player's location
        y (int) the y of the player's location
        z (int) the z of the player's location
        returns
        (bool) true if location is valid
        """
        return (
            x >= self.minx-1
            and x <= self.maxx+1
            and y >= self.miny - 1
            and y <= self.maxy + 1
            and z >= self.minz
            and z <= self.maxz
        )

class Zone(BaseMapObj):
    """an internal zone class"""
    def __init__(self, minx, maxx, miny, maxy, minz, maxz, name):
        super(Zone, self).__init__(minx, maxx, miny, maxy, minz, maxz, "zone")
        self.zonename = name
