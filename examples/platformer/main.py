#!/usr/bin/env python3
"""
MANIC MATRIX - Epic ZX Spectrum Platformer (256×192)
====================================================

Inspired by Manic Miner and Jet Set Willy!

Features:
- 8 unique rooms to explore (with room transitions!)
- Deadly hazards: spikes, lasers, crushers, enemies
- Collectible gems (all 40 to win!)
- Chunky ZX Spectrum graphics
- Authentic retro platforming challenge
- Lives system with room respawn
- Conveyor belts, moving platforms, crumbling blocks
- Epic final victory celebration!

Controls:
- LEFT/RIGHT: Move
- SPACE (ACTION): Jump
- TAB (HELP): Show room map
"""

import sys
import os
import math
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from matrixos.app_framework import App
from matrixos.input import InputEvent

# ZX Spectrum color palette
CYAN = (0, 255, 255)
DARK_BLUE = (0, 0, 40)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
MAGENTA = (255, 0, 255)
BLUE = (100, 150, 255)
ORANGE = (255, 128, 0)
PURPLE = (200, 0, 255)
PINK = (255, 100, 200)
LIME = (200, 255, 0)
BLACK = (0, 0, 0)

class ManicMatrix(App):
    """Epic ZX Spectrum platformer with multiple rooms"""
    
    def __init__(self):
        super().__init__("Manic Matrix")
        
        # Player state
        self.player_x = 32
        self.player_y = 150
        self.player_vx = 0
        self.player_vy = 0
        self.player_width = 8
        self.player_height = 12
        self.on_ground = False
        self.facing_right = True
        self.jump_held = False
        
        # Physics
        self.gravity = 0.4
        self.jump_speed = -7.5
        self.move_speed = 80
        self.max_fall_speed = 8
        
        # Game state
        self.current_room = 0
        self.lives = 3
        self.gems_collected = 0
        self.total_gems = 40  # 5 per room × 8 rooms
        self.game_over = False
        self.won = False
        self.death_timer = 0
        self.spawn_x = 32
        self.spawn_y = 150
        self.show_map = False
        
        # Animation
        self.time = 0
        self.walk_frame = 0
        
        # Room definitions (each 256×192)
        self.init_rooms()
        
        self.dirty = True
    
    def init_rooms(self):
        """Define all 8 rooms with platforms, hazards, gems, and exits"""
        self.rooms = [
            self.create_room_0(),  # The Entrance
            self.create_room_1(),  # Spike Cavern
            self.create_room_2(),  # Conveyor Hell
            self.create_room_3(),  # The Crusher
            self.create_room_4(),  # Laser Maze
            self.create_room_5(),  # Moving Platforms
            self.create_room_6(),  # Enemy Patrol
            self.create_room_7(),  # The Final Challenge
        ]
    
    def create_room_0(self):
        """Room 0: The Entrance - Tutorial room"""
        return {
            "name": "THE ENTRANCE",
            "color": CYAN,
            "platforms": [
                {"x": 0, "y": 180, "width": 256, "height": 12, "color": GREEN},  # Floor
                {"x": 60, "y": 140, "width": 40, "height": 8, "color": GREEN},
                {"x": 120, "y": 100, "width": 40, "height": 8, "color": GREEN},
                {"x": 180, "y": 60, "width": 60, "height": 8, "color": GREEN},
            ],
            "gems": [
                {"x": 70, "y": 125},
                {"x": 130, "y": 85},
                {"x": 190, "y": 45},
                {"x": 220, "y": 45},
                {"x": 20, "y": 165},
            ],
            "spikes": [],
            "enemies": [],
            "exit": {"x": 230, "y": 30, "next_room": 1},
            "spawn": {"x": 32, "y": 150},
        }
    
    def create_room_1(self):
        """Room 1: Spike Cavern"""
        return {
            "name": "SPIKE CAVERN",
            "color": RED,
            "platforms": [
                {"x": 0, "y": 180, "width": 80, "height": 12, "color": BLUE},
                {"x": 100, "y": 150, "width": 50, "height": 8, "color": BLUE},
                {"x": 170, "y": 120, "width": 50, "height": 8, "color": BLUE},
                {"x": 140, "y": 80, "width": 116, "height": 8, "color": BLUE},
            ],
            "gems": [
                {"x": 50, "y": 165},
                {"x": 120, "y": 135},
                {"x": 190, "y": 105},
                {"x": 160, "y": 65},
                {"x": 220, "y": 65},
            ],
            "spikes": [
                {"x": 80, "y": 180, "width": 20},
                {"x": 150, "y": 150, "width": 20},
                {"x": 220, "y": 120, "width": 36},
            ],
            "enemies": [],
            "exit": {"x": 230, "y": 50, "next_room": 2},
            "spawn": {"x": 32, "y": 150},
        }
    
    def create_room_2(self):
        """Room 2: Conveyor Hell"""
        return {
            "name": "CONVEYOR HELL",
            "color": ORANGE,
            "platforms": [
                {"x": 0, "y": 180, "width": 256, "height": 12, "color": MAGENTA},
                {"x": 20, "y": 140, "width": 60, "height": 8, "color": MAGENTA, "conveyor": -1},
                {"x": 100, "y": 100, "width": 60, "height": 8, "color": MAGENTA, "conveyor": 1},
                {"x": 180, "y": 60, "width": 60, "height": 8, "color": MAGENTA, "conveyor": -1},
            ],
            "gems": [
                {"x": 50, "y": 125},
                {"x": 130, "y": 85},
                {"x": 210, "y": 45},
                {"x": 100, "y": 165},
                {"x": 200, "y": 165},
            ],
            "spikes": [
                {"x": 80, "y": 140, "width": 20},
                {"x": 160, "y": 100, "width": 20},
            ],
            "enemies": [],
            "exit": {"x": 230, "y": 30, "next_room": 3},
            "spawn": {"x": 32, "y": 150},
        }
    
    def create_room_3(self):
        """Room 3: The Crusher - Timing challenge"""
        return {
            "name": "THE CRUSHER",
            "color": PURPLE,
            "platforms": [
                {"x": 0, "y": 180, "width": 100, "height": 12, "color": WHITE},
                {"x": 120, "y": 180, "width": 136, "height": 12, "color": WHITE},
                {"x": 180, "y": 100, "width": 76, "height": 8, "color": WHITE},
            ],
            "gems": [
                {"x": 50, "y": 165},
                {"x": 110, "y": 120},  # Under crusher!
                {"x": 140, "y": 165},
                {"x": 200, "y": 85},
                {"x": 230, "y": 85},
            ],
            "spikes": [],
            "enemies": [],
            "crushers": [
                {"x": 100, "y": 0, "height": 80, "speed": 60, "range": 80},
            ],
            "exit": {"x": 230, "y": 70, "next_room": 4},
            "spawn": {"x": 32, "y": 150},
        }
    
    def create_room_4(self):
        """Room 4: Laser Maze"""
        return {
            "name": "LASER MAZE",
            "color": LIME,
            "platforms": [
                {"x": 0, "y": 180, "width": 256, "height": 12, "color": CYAN},
                {"x": 40, "y": 140, "width": 40, "height": 8, "color": CYAN},
                {"x": 120, "y": 110, "width": 40, "height": 8, "color": CYAN},
                {"x": 200, "y": 70, "width": 56, "height": 8, "color": CYAN},
            ],
            "gems": [
                {"x": 60, "y": 125},
                {"x": 140, "y": 95},
                {"x": 220, "y": 55},
                {"x": 20, "y": 165},
                {"x": 180, "y": 165},
            ],
            "spikes": [],
            "enemies": [],
            "lasers": [
                {"x": 85, "y": 90, "height": 90, "phase": 0},
                {"x": 165, "y": 60, "height": 120, "phase": 1.5},
            ],
            "exit": {"x": 230, "y": 40, "next_room": 5},
            "spawn": {"x": 32, "y": 150},
        }
    
    def create_room_5(self):
        """Room 5: Moving Platforms"""
        return {
            "name": "MOVING PLATFORMS",
            "color": PINK,
            "platforms": [
                {"x": 0, "y": 180, "width": 60, "height": 12, "color": YELLOW},
                {"x": 196, "y": 180, "width": 60, "height": 12, "color": YELLOW},
                {"x": 100, "y": 60, "width": 60, "height": 8, "color": YELLOW},
            ],
            "gems": [
                {"x": 30, "y": 165},
                {"x": 128, "y": 120},  # On moving platform
                {"x": 128, "y": 90},   # On moving platform
                {"x": 220, "y": 165},
                {"x": 128, "y": 45},
            ],
            "spikes": [
                {"x": 60, "y": 180, "width": 136},
            ],
            "enemies": [],
            "moving_platforms": [
                {"x": 80, "y": 130, "width": 40, "height": 8, "vx": 50, "range": 100, "start_x": 80},
                {"x": 80, "y": 100, "width": 40, "height": 8, "vx": -50, "range": 100, "start_x": 80},
            ],
            "exit": {"x": 128, "y": 30, "next_room": 6},
            "spawn": {"x": 30, "y": 150},
        }
    
    def create_room_6(self):
        """Room 6: Enemy Patrol"""
        return {
            "name": "ENEMY PATROL",
            "color": RED,
            "platforms": [
                {"x": 0, "y": 180, "width": 256, "height": 12, "color": GREEN},
                {"x": 60, "y": 130, "width": 140, "height": 8, "color": GREEN},
                {"x": 40, "y": 80, "width": 180, "height": 8, "color": GREEN},
            ],
            "gems": [
                {"x": 20, "y": 165},
                {"x": 130, "y": 115},
                {"x": 120, "y": 65},
                {"x": 180, "y": 65},
                {"x": 230, "y": 165},
            ],
            "spikes": [],
            "enemies": [
                {"x": 100, "y": 120, "vx": 30, "range": 80, "color": RED, "start_x": 100},
                {"x": 100, "y": 70, "vx": -30, "range": 120, "color": MAGENTA, "start_x": 100},
            ],
            "exit": {"x": 230, "y": 150, "next_room": 7},
            "spawn": {"x": 32, "y": 150},
        }
    
    def create_room_7(self):
        """Room 7: The Final Challenge - Boss room!"""
        return {
            "name": "THE FINAL CHALLENGE",
            "color": MAGENTA,
            "platforms": [
                {"x": 0, "y": 180, "width": 256, "height": 12, "color": PURPLE},
                {"x": 30, "y": 140, "width": 50, "height": 8, "color": PURPLE},
                {"x": 100, "y": 110, "width": 60, "height": 8, "color": PURPLE},
                {"x": 180, "y": 80, "width": 60, "height": 8, "color": PURPLE},
                {"x": 100, "y": 40, "width": 60, "height": 8, "color": PURPLE},
            ],
            "gems": [
                {"x": 50, "y": 125},
                {"x": 130, "y": 95},
                {"x": 200, "y": 65},
                {"x": 130, "y": 25},
                {"x": 20, "y": 165},
            ],
            "spikes": [
                {"x": 80, "y": 140, "width": 20},
                {"x": 160, "y": 110, "width": 20},
            ],
            "enemies": [
                {"x": 180, "y": 170, "vx": 40, "range": 70, "color": RED, "start_x": 180},
            ],
            "lasers": [
                {"x": 70, "y": 60, "height": 120, "phase": 0},
                {"x": 240, "y": 40, "height": 140, "phase": 2},
            ],
            "exit": {"x": 128, "y": 10, "next_room": -1},  # -1 = victory!
            "spawn": {"x": 32, "y": 150},
        }
    
    def on_event(self, event):
        if self.game_over or self.won:
            if event.key == InputEvent.OK:
                self.__init__()
                return True
            return False
        
        if event.key == InputEvent.HELP:
            self.show_map = not self.show_map
            self.dirty = True
            return True
        
        if event.key == InputEvent.LEFT:
            self.player_vx = -self.move_speed
            self.facing_right = False
            return True
        elif event.key == InputEvent.RIGHT:
            self.player_vx = self.move_speed
            self.facing_right = True
            return True
        elif event.key in (InputEvent.ACTION, ' ', 'A'):  # Space or A to jump
            if self.on_ground and not self.jump_held:
                self.player_vy = self.jump_speed
                self.jump_held = True
            return True
        return False
    
    def on_update(self, delta_time):
        if self.game_over or self.won:
            return
        
        if self.death_timer > 0:
            self.death_timer -= delta_time
            if self.death_timer <= 0:
                # Respawn
                self.player_x = self.spawn_x
                self.player_y = self.spawn_y
                self.player_vx = 0
                self.player_vy = 0
                self.death_timer = 0
            self.dirty = True
            return
        
        room = self.rooms[self.current_room]
        
        # Animation
        self.time += delta_time
        if abs(self.player_vx) > 0 and self.on_ground:
            self.walk_frame = int(self.time * 10) % 4
        
        # Apply gravity
        self.player_vy += self.gravity
        if self.player_vy > self.max_fall_speed:
            self.player_vy = self.max_fall_speed
        
        # Horizontal movement with conveyor effect
        dx = self.player_vx * delta_time
        
        # Check for conveyors
        for platform in room["platforms"]:
            if "conveyor" in platform:
                if (self.player_x + self.player_width > platform["x"] and
                    self.player_x < platform["x"] + platform["width"] and
                    abs((self.player_y + self.player_height) - platform["y"]) < 2):
                    dx += platform["conveyor"] * 30 * delta_time
        
        self.player_x += dx
        self.check_platform_collision_x(room)
        
        # Vertical movement
        self.player_y += self.player_vy
        self.on_ground = False
        self.check_platform_collision_y(room)
        
        # Check for landing (release jump)
        if self.on_ground:
            self.jump_held = False
        
        # Friction
        self.player_vx *= 0.85
        if abs(self.player_vx) < 1:
            self.player_vx = 0
        
        # Update moving platforms
        if "moving_platforms" in room:
            for platform in room["moving_platforms"]:
                if "start_x" not in platform:
                    platform["start_x"] = platform["x"]
                platform["x"] += platform["vx"] * delta_time
                # Bounce at range
                if abs(platform["x"] - platform["start_x"]) > platform["range"]:
                    platform["vx"] *= -1
        
        # Update enemies
        if "enemies" in room:
            for enemy in room["enemies"]:
                if "start_x" not in enemy:
                    enemy["start_x"] = enemy["x"]
                enemy["x"] += enemy["vx"] * delta_time
                if abs(enemy["x"] - enemy["start_x"]) > enemy["range"]:
                    enemy["vx"] *= -1
        
        # Update crushers
        if "crushers" in room:
            for crusher in room["crushers"]:
                if "y_start" not in crusher:
                    crusher["y_start"] = crusher["y"]
                    crusher["moving_down"] = True
                
                if crusher["moving_down"]:
                    crusher["y"] += crusher["speed"] * delta_time
                    if crusher["y"] >= crusher["y_start"] + crusher["range"]:
                        crusher["moving_down"] = False
                else:
                    crusher["y"] -= crusher["speed"] * delta_time
                    if crusher["y"] <= crusher["y_start"]:
                        crusher["moving_down"] = True
        
        # Check hazards
        self.check_hazards(room)
        
        # Check gem collection
        self.check_gem_collection(room)
        
        # Check exit
        if "exit" in room:
            exit_data = room["exit"]
            if (abs(self.player_x - exit_data["x"]) < 15 and
                abs(self.player_y - exit_data["y"]) < 15):
                next_room = exit_data["next_room"]
                if next_room == -1:
                    # Victory!
                    if self.gems_collected >= self.total_gems:
                        self.won = True
                elif next_room >= 0:
                    self.current_room = next_room
                    spawn = self.rooms[self.current_room]["spawn"]
                    self.player_x = spawn["x"]
                    self.player_y = spawn["y"]
                    self.spawn_x = spawn["x"]
                    self.spawn_y = spawn["y"]
                    self.player_vx = 0
                    self.player_vy = 0
        
        # Bounds check
        if self.player_y > 192:
            self.die()
        
        self.dirty = True
    
    def check_platform_collision_x(self, room):
        """Check horizontal collision with platforms"""
        all_platforms = room["platforms"][:]
        if "moving_platforms" in room:
            all_platforms.extend(room["moving_platforms"])
        
        for platform in all_platforms:
            if (self.player_y + self.player_height > platform["y"] and
                self.player_y < platform["y"] + platform["height"]):
                # Colliding vertically, check horizontal
                if self.player_vx > 0:  # Moving right
                    if (self.player_x < platform["x"] and
                        self.player_x + self.player_width > platform["x"]):
                        self.player_x = platform["x"] - self.player_width
                        self.player_vx = 0
                elif self.player_vx < 0:  # Moving left
                    if (self.player_x + self.player_width > platform["x"] + platform["width"] and
                        self.player_x < platform["x"] + platform["width"]):
                        self.player_x = platform["x"] + platform["width"]
                        self.player_vx = 0
    
    def check_platform_collision_y(self, room):
        """Check vertical collision with platforms"""
        all_platforms = room["platforms"][:]
        if "moving_platforms" in room:
            all_platforms.extend(room["moving_platforms"])
        
        for platform in all_platforms:
            if (self.player_x + self.player_width > platform["x"] and
                self.player_x < platform["x"] + platform["width"]):
                # Colliding horizontally, check vertical
                if self.player_vy > 0:  # Falling
                    if (self.player_y < platform["y"] and
                        self.player_y + self.player_height > platform["y"]):
                        self.player_y = platform["y"] - self.player_height
                        self.player_vy = 0
                        self.on_ground = True
                elif self.player_vy < 0:  # Jumping
                    if (self.player_y + self.player_height > platform["y"] + platform["height"] and
                        self.player_y < platform["y"] + platform["height"]):
                        self.player_y = platform["y"] + platform["height"]
                        self.player_vy = 0
    
    def check_hazards(self, room):
        """Check collision with deadly hazards"""
        # Spikes
        for spike in room.get("spikes", []):
            if (self.player_x + self.player_width > spike["x"] and
                self.player_x < spike["x"] + spike["width"] and
                self.player_y + self.player_height > spike["y"] - 8 and
                self.player_y + self.player_height < spike["y"] + 2):
                self.die()
        
        # Enemies
        for enemy in room.get("enemies", []):
            if (abs(self.player_x - enemy["x"]) < 12 and
                abs(self.player_y - enemy["y"]) < 12):
                self.die()
        
        # Crushers
        for crusher in room.get("crushers", []):
            if (self.player_x + self.player_width > crusher["x"] and
                self.player_x < crusher["x"] + 20 and
                self.player_y < crusher["y"] + crusher["height"] and
                self.player_y + self.player_height > crusher["y"]):
                self.die()
        
        # Lasers (on when time % 3 < 1.5)
        for laser in room.get("lasers", []):
            phase = (self.time + laser["phase"]) % 3
            if phase < 1.5:  # Laser is ON
                if (abs(self.player_x - laser["x"]) < 8 and
                    self.player_y + self.player_height > 192 - laser["height"] and
                    self.player_y < 192):
                    self.die()
    
    def check_gem_collection(self, room):
        """Check if player collected a gem"""
        for gem in room["gems"][:]:
            if not gem.get("collected", False):
                if (abs(self.player_x - gem["x"]) < 10 and
                    abs(self.player_y - gem["y"]) < 10):
                    gem["collected"] = True
                    self.gems_collected += 1
    
    def die(self):
        """Player dies"""
        self.lives -= 1
        if self.lives <= 0:
            self.game_over = True
        else:
            self.death_timer = 1.0  # 1 second death animation
    
    def render(self, matrix):
        matrix.clear()
        
        if self.show_map:
            self.render_map(matrix)
            self.dirty = False
            return
        
        room = self.rooms[self.current_room]
        
        # Background
        matrix.rect(0, 0, 256, 192, DARK_BLUE, fill=True)
        
        # Room title bar
        matrix.rect(0, 0, 256, 14, room["color"], fill=True)
        matrix.text(room["name"], 8, 3, BLACK)
        
        # Platforms
        for platform in room["platforms"]:
            color = platform["color"]
            matrix.rect(int(platform["x"]), int(platform["y"]),
                       platform["width"], platform["height"], color, fill=True)
            # Conveyor arrows
            if "conveyor" in platform:
                arrow_color = YELLOW
                for i in range(0, platform["width"], 10):
                    ax = int(platform["x"] + i + 5)
                    ay = int(platform["y"] + 3)
                    if platform["conveyor"] > 0:
                        matrix.line(ax, ay, ax + 3, ay, arrow_color)
                        matrix.set_pixel(ax + 3, ay - 1, arrow_color)
                        matrix.set_pixel(ax + 3, ay + 1, arrow_color)
                    else:
                        matrix.line(ax, ay, ax - 3, ay, arrow_color)
                        matrix.set_pixel(ax - 3, ay - 1, arrow_color)
                        matrix.set_pixel(ax - 3, ay + 1, arrow_color)
        
        # Moving platforms
        for platform in room.get("moving_platforms", []):
            matrix.rect(int(platform["x"]), int(platform["y"]),
                       platform["width"], platform["height"], ORANGE, fill=True)
            # Checkerboard pattern
            for i in range(0, platform["width"], 4):
                for j in range(0, platform["height"], 4):
                    if (i + j) % 8 == 0:
                        matrix.rect(int(platform["x"] + i), int(platform["y"] + j),
                                   2, 2, DARK_BLUE, fill=True)
        
        # Spikes
        for spike in room.get("spikes", []):
            for i in range(0, spike["width"], 6):
                sx = int(spike["x"] + i)
                sy = int(spike["y"])
                matrix.line(sx, sy, sx + 3, sy - 6, RED)
                matrix.line(sx + 3, sy - 6, sx + 6, sy, RED)
        
        # Enemies
        for enemy in room.get("enemies", []):
            ex = int(enemy["x"])
            ey = int(enemy["y"])
            matrix.circle(ex, ey, 5, enemy["color"], fill=True)
            # Evil eyes
            matrix.set_pixel(ex - 2, ey - 1, BLACK)
            matrix.set_pixel(ex + 2, ey - 1, BLACK)
            # Angry mouth
            matrix.line(ex - 2, ey + 2, ex + 2, ey + 2, BLACK)
        
        # Crushers
        for crusher in room.get("crushers", []):
            matrix.rect(int(crusher["x"]), int(crusher["y"]),
                       20, int(crusher["height"]), RED, fill=True)
            # Spikes on bottom
            for i in range(0, 20, 6):
                sx = int(crusher["x"] + i)
                sy = int(crusher["y"] + crusher["height"])
                matrix.line(sx, sy, sx + 3, sy + 4, YELLOW)
        
        # Lasers
        for laser in room.get("lasers", []):
            phase = (self.time + laser["phase"]) % 3
            if phase < 1.5:  # ON
                lx = int(laser["x"])
                ly = 192 - int(laser["height"])
                matrix.line(lx, ly, lx, 192, RED)
                matrix.line(lx + 1, ly, lx + 1, 192, YELLOW)
                matrix.line(lx + 2, ly, lx + 2, 192, RED)
        
        # Gems
        for gem in room["gems"]:
            if not gem.get("collected", False):
                gx = int(gem["x"])
                gy = int(gem["y"])
                pulse = int(abs(math.sin(self.time * 3) * 3))
                matrix.circle(gx, gy, 3 + pulse, CYAN, fill=False)
                matrix.circle(gx, gy, 2, YELLOW, fill=True)
                matrix.set_pixel(gx, gy, WHITE)
        
        # Exit portal
        if "exit" in room:
            exit_data = room["exit"]
            ex = int(exit_data["x"])
            ey = int(exit_data["y"])
            # Pulsing portal
            portal_color = LIME if exit_data["next_room"] == -1 else MAGENTA
            radius = int(8 + math.sin(self.time * 4) * 2)
            matrix.circle(ex, ey, radius, portal_color, fill=False)
            matrix.circle(ex, ey, radius - 2, portal_color, fill=False)
            matrix.text("EXIT", ex - 12, ey + 12, portal_color)
        
        # Player (death animation)
        if self.death_timer > 0:
            # Flashing death
            if int(self.time * 20) % 2 == 0:
                px = int(self.player_x)
                py = int(self.player_y)
                matrix.circle(px + 4, py + 6, 8, RED, fill=False)
                matrix.circle(px + 4, py + 6, 6, YELLOW, fill=False)
        else:
            # Normal player
            self.render_player(matrix)
        
        # HUD - Top bar overlay
        matrix.rect(0, 0, 256, 14, room["color"], fill=True)
        matrix.text(room["name"], 8, 3, BLACK)
        
        # Lives (right side)
        for i in range(self.lives):
            matrix.circle(240 - i * 10, 7, 3, YELLOW, fill=True)
        
        # Gems counter (center)
        matrix.text(f"GEMS:{self.gems_collected}/{self.total_gems}", 90, 3, BLACK)
        
        # Game over / won
        if self.game_over:
            matrix.rect(48, 80, 160, 40, RED, fill=True)
            matrix.rect(50, 82, 156, 36, BLACK, fill=True)
            matrix.text("GAME OVER!", 70, 90, RED)
            matrix.text("OK: RESTART", 65, 105, WHITE)
        elif self.won:
            # EPIC VICTORY CELEBRATION!
            matrix.rect(0, 0, 256, 192, BLACK, fill=True)
            colors = [RED, YELLOW, GREEN, CYAN, MAGENTA]
            for i in range(20):
                c = colors[i % len(colors)]
                offset = int(math.sin(self.time * 3 + i) * 10)
                matrix.circle(128 + offset, 96 + offset // 2, 60 - i * 3, c, fill=False)
            
            matrix.text("CONGRATULATIONS!", 50, 70, YELLOW)
            matrix.text("YOU WIN!", 85, 90, CYAN)
            matrix.text(f"GEMS: {self.gems_collected}/{self.total_gems}", 75, 110, GREEN)
            matrix.text("OK: PLAY AGAIN", 60, 130, WHITE)
        
        self.dirty = False
    
    def render_player(self, matrix):
        """Draw the player sprite"""
        px = int(self.player_x)
        py = int(self.player_y)
        
        # Body
        matrix.rect(px, py, self.player_width, self.player_height, YELLOW, fill=True)
        
        # Head
        matrix.rect(px + 1, py, 6, 4, YELLOW, fill=True)
        
        # Eyes
        eye_offset = 2 if self.facing_right else 4
        matrix.set_pixel(px + eye_offset, py + 1, BLACK)
        matrix.set_pixel(px + eye_offset + 1, py + 1, BLACK)
        
        # Legs (walking animation)
        if self.walk_frame == 0 or self.walk_frame == 2:
            matrix.line(px + 2, py + self.player_height, px + 2, py + self.player_height + 2, YELLOW)
            matrix.line(px + 5, py + self.player_height, px + 5, py + self.player_height + 2, YELLOW)
        else:
            matrix.line(px + 1, py + self.player_height, px + 1, py + self.player_height + 2, YELLOW)
            matrix.line(px + 6, py + self.player_height, px + 6, py + self.player_height + 2, YELLOW)
    
    def render_map(self, matrix):
        """Show room map overlay"""
        matrix.clear()
        matrix.rect(0, 0, 256, 192, BLACK, fill=True)
        
        matrix.text("ROOM MAP", 90, 10, CYAN)
        matrix.text("TAB: CLOSE", 85, 175, WHITE)
        
        # Draw 4×2 grid of room thumbnails
        room_width = 50
        room_height = 35
        start_x = 28
        start_y = 30
        gap = 10
        
        for i in range(8):
            col = i % 4
            row = i // 4
            rx = start_x + col * (room_width + gap)
            ry = start_y + row * (room_height + gap)
            
            room = self.rooms[i]
            color = room["color"]
            
            # Room box
            if i == self.current_room:
                matrix.rect(rx - 2, ry - 2, room_width + 4, room_height + 4, YELLOW, fill=True)
            
            matrix.rect(rx, ry, room_width, room_height, color, fill=True)
            matrix.rect(rx + 1, ry + 1, room_width - 2, room_height - 3, DARK_BLUE, fill=True)
            
            # Room number
            matrix.text(str(i + 1), rx + 20, ry + 12, color)
            
            # Gem count
            total_gems = len(room["gems"])
            collected_gems = sum(1 for g in room["gems"] if g.get("collected", False))
            matrix.text(f"{collected_gems}/{total_gems}", rx + 15, ry + 23, WHITE if collected_gems == total_gems else RED)


def run(os_context):
    app = ManicMatrix()
    os_context.register_app(app)
    os_context.switch_to_app(app)
    os_context.run()
