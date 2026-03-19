# dungeon_crawler_timebased.py
import time
import random
import json
import os
from collections import deque

class RandomDungeon:
    def __init__(self, stats_manager):
        self.stats_manager = stats_manager
        self.stats = stats_manager.stats
        self.player_x = 1
        self.player_y = 1
        
        self.running = True
        self.message = "Time-based movement! Plan your moves!"
        self.steps_taken = 0
        self.treasure_found = 0
        self.game_over = False
        self.death_message = ""
        self.death_cause = None
        
        # Turn tracking
        self.current_turn = 0
        
        # Fire cycle tracking
        self.fire_cycle = 0  # 0-5: 0-2 = fire ON, 3-5 = fire OFF
        
        # Snail tracking
        self.snail_active = False
        self.snail_x = -1
        self.snail_y = -1
        self.snail_move_counter = 0
        self.snail_speed = 10  # Moves every 10 turns
        self.snail_level_appeared = 7
        
        self.width = 12
        self.height = 12
        
        self.world = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.fire_map = [[False for _ in range(self.width)] for _ in range(self.height)]
        self.monster_positions = []
        self.generate_dungeon()
        
        # Activate snail if dungeon count >= 7
        self.check_snail_activation()
    
    def check_snail_activation(self):
        """Activate snail based on dungeon count"""
        dungeon_num = self.stats['dungeons_completed'] + 1
        if dungeon_num >= self.snail_level_appeared:
            self.snail_active = True
            self.calculate_snail_speed(dungeon_num)
            self.place_snail()
    
    def calculate_snail_speed(self, dungeon_num):
        """Calculate snail speed based on dungeon level"""
        levels_above_7 = max(0, dungeon_num - 7)
        speed_reduction = levels_above_7 // 5
        self.snail_speed = max(3, 10 - speed_reduction)
    
    def place_snail(self):
        """Place snail in a random open space"""
        attempts = 0
        while attempts < 100:
            x = random.randint(2, self.width-3)
            y = random.randint(2, self.height-3)
            
            if (self.world[y][x] == 0 and 
                (x, y) != (1, 1) and 
                (x, y) != (self.width-2, self.height-2) and
                not any((x, y) == (mx, my) for mx, my in self.monster_positions)):
                
                if abs(x - self.player_x) + abs(y - self.player_y) > 3:
                    self.snail_x, self.snail_y = x, y
                    return
            attempts += 1
        
        self.snail_x, self.snail_y = 2, 2
    
    def get_avatar(self):
        """Return the appropriate avatar based on dungeons completed"""
        completed = self.stats['dungeons_completed']
        
        if completed <= 2:
            return "👤"
        elif completed <= 7:
            return "👨‍🎓"
        elif completed <= 12:
            return "👩‍🍳"
        elif completed <= 17:
            return "👨‍🚒"
        elif completed <= 23:
            return "👮‍♂️"
        elif completed <= 27:
            return "🥷"
        elif completed <= 33:
            return "🧙‍♂️"
        else:
            return "🦸‍♂️"
    
    def get_avatar_name(self):
        """Return the name of current avatar"""
        completed = self.stats['dungeons_completed']
        
        if completed <= 2:
            return "Indistinct Goon"
        elif completed <= 7:
            return "Learner"
        elif completed <= 12:
            return "Chef"
        elif completed <= 13:
            return "Firefighter"
        elif completed <= 18:
            return "Police Officer"
        elif completed <= 24:
            return "Ninja"
        elif completed <= 28:
            return "Wizard"
        else:
            return "Superhero"
    
    def simple_clear(self):
        print("\n" + "=" * 50 + "\n")
    
    def generate_dungeon(self):
        """Generate a random but ALWAYS solvable dungeon"""
        # Create border walls
        for i in range(self.height):
            for j in range(self.width):
                if i == 0 or i == self.height-1 or j == 0 or j == self.width-1:
                    self.world[i][j] = 1
        
        exit_x = self.width - 2
        exit_y = self.height - 2
        
        # Create path
        path = self.create_path(1, 1, exit_x, exit_y)
        
        # Add random walls (never block path)
        for _ in range(15):
            while True:
                x = random.randint(2, self.width-3)
                y = random.randint(2, self.height-3)
                if (x, y) not in path and (x, y) != (1, 1):
                    self.world[y][x] = 1
                    break
        
        # Add treasures on path
        path_list = list(path)
        random.shuffle(path_list)
        
        treasures_added = 0
        for x, y in path_list:
            if treasures_added < 4 and (x, y) != (1, 1) and (x, y) != (exit_x, exit_y):
                self.world[y][x] = 2
                treasures_added += 1
        
        self.total_treasures = treasures_added
        
        # Add monsters (fire creatures)
        self.monster_positions = []
        for _ in range(3):
            attempts = 0
            while attempts < 50:
                x = random.randint(2, self.width-3)
                y = random.randint(2, self.height-3)
                if (self.world[y][x] == 0 and 
                    (x, y) != (1, 1) and 
                    (x, y) != (exit_x, exit_y)):
                    self.world[y][x] = 3
                    self.monster_positions.append((x, y))
                    break
                attempts += 1
        
        # Place exit
        self.world[exit_y][exit_x] = 4
        
        # Ensure player start is empty
        self.world[1][1] = 0
    
    def create_path(self, start_x, start_y, end_x, end_y):
        """Create a guaranteed path from start to exit"""
        path = set()
        current_x, current_y = start_x, start_y
        path.add((current_x, current_y))
        
        attempts = 0
        max_attempts = 1000
        
        while (current_x, current_y) != (end_x, end_y) and attempts < max_attempts:
            attempts += 1
            possible_moves = []
            
            if current_x < end_x:
                possible_moves.append((1, 0))
            if current_x > end_x:
                possible_moves.append((-1, 0))
            if current_y < end_y:
                possible_moves.append((0, 1))
            if current_y > end_y:
                possible_moves.append((0, -1))
            
            if random.random() < 0.3:
                possible_moves = [(1,0), (-1,0), (0,1), (0,-1)]
            
            random.shuffle(possible_moves)
            moved = False
            
            for dx, dy in possible_moves:
                new_x = current_x + dx
                new_y = current_y + dy
                
                if (1 <= new_x < self.width-1 and 1 <= new_y < self.height-1):
                    current_x, current_y = new_x, new_y
                    path.add((current_x, current_y))
                    moved = True
                    break
            
            if not moved:
                for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
                    new_x = current_x + dx
                    new_y = current_y + dy
                    if (1 <= new_x < self.width-1 and 1 <= new_y < self.height-1):
                        current_x, current_y = new_x, new_y
                        path.add((current_x, current_y))
                        break
        
        return path
    
    def get_next_fire_state(self):
        """Determine what the fire state will be NEXT turn"""
        next_cycle = (self.fire_cycle + 1) % 6
        return next_cycle < 3  # True if fire will be active next turn
    
    def get_next_fire_map(self):
        """Generate the fire map for NEXT turn"""
        next_fire_map = [[False for _ in range(self.width)] for _ in range(self.height)]
        next_cycle = (self.fire_cycle + 1) % 6
        fire_active_next = (next_cycle < 3)
        
        if fire_active_next:
            for mx, my in self.monster_positions:
                directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
                for dx, dy in directions:
                    fx, fy = mx + dx, my + dy
                    if (0 <= fx < self.width and 0 <= fy < self.height and 
                        self.world[fy][fx] != 1):
                        next_fire_map[fy][fx] = True
        
        return next_fire_map
    
    def get_next_snail_position(self):
        """Determine where snail will be NEXT turn"""
        if not self.snail_active or self.snail_x == -1:
            return (self.snail_x, self.snail_y)
        
        # Check if snail will move this upcoming turn
        will_snail_move = ((self.snail_move_counter + 1) >= self.snail_speed)
        
        if not will_snail_move:
            return (self.snail_x, self.snail_y)
        
        # Calculate snail's next position
        path = self.find_path_to_player()
        if path and len(path) > 1:
            next_x, next_y = path[1]
            # Check if next position is valid
            if (self.world[next_y][next_x] != 1 and 
                self.world[next_y][next_x] != 3):
                return (next_x, next_y)
        
        return (self.snail_x, self.snail_y)
    
    def find_path_to_player(self):
        """BFS pathfinding from snail to player"""
        if self.snail_x == -1:
            return None
        
        queue = deque([(self.snail_x, self.snail_y, [(self.snail_x, self.snail_y)])])
        visited = {(self.snail_x, self.snail_y)}
        
        while queue:
            x, y, path = queue.popleft()
            
            if x == self.player_x and y == self.player_y:
                return path
            
            for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
                new_x, new_y = x + dx, y + dy
                
                if (0 <= new_x < self.width and 0 <= new_y < self.height and
                    (new_x, new_y) not in visited):
                    
                    if (self.world[new_y][new_x] != 1 and
                        self.world[new_y][new_x] != 3):
                        
                        visited.add((new_x, new_y))
                        new_path = path + [(new_x, new_y)]
                        queue.append((new_x, new_y, new_path))
        
        return None
    
    def advance_turn(self):
        """Advance to next turn (called after player commits to move)"""
        self.current_turn += 1
        self.steps_taken += 1
        
        # Update fire cycle
        self.fire_cycle = (self.fire_cycle + 1) % 6
        
        # Update current fire map for display
        fire_active = (self.fire_cycle < 3)
        for y in range(self.height):
            for x in range(self.width):
                self.fire_map[y][x] = False
        
        if fire_active:
            for mx, my in self.monster_positions:
                directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
                for dx, dy in directions:
                    fx, fy = mx + dx, my + dy
                    if (0 <= fx < self.width and 0 <= fy < self.height and 
                        self.world[fy][fx] != 1):
                        self.fire_map[fy][fx] = True
        
        # Update snail movement counter and move if needed
        if self.snail_active and self.snail_x != -1:
            self.snail_move_counter += 1
            if self.snail_move_counter >= self.snail_speed:
                self.snail_move_counter = 0
                path = self.find_path_to_player()
                if path and len(path) > 1:
                    next_x, next_y = path[1]
                    if (self.world[next_y][next_x] != 1 and 
                        self.world[next_y][next_x] != 3):
                        self.snail_x, self.snail_y = next_x, next_y
    
    def draw(self):
        """Draw the game"""
        self.simple_clear()
        
        avatar = self.get_avatar()
        avatar_name = self.get_avatar_name()
        dungeon_num = self.stats['dungeons_completed'] + 1
        
        print("⏱️  TIME-BASED DUNGEON CRAWLER ⏱️")
        print(f"Dungeon #{dungeon_num}")
        print(f"Avatar: {avatar} {avatar_name}")
        print(f"Turn: {self.current_turn}")
        
        # Show fire status
        fire_status = "🔥 ACTIVE" if self.fire_cycle < 3 else "💨 cooling"
        next_status = "🔥 will be ACTIVE" if self.get_next_fire_state() else "💨 will be cooling"
        print(f"Fire NOW: {fire_status} | NEXT: {next_status}")
        
        if self.snail_active:
            speed_text = f"moves every {self.snail_speed} turns"
            moves_next = (self.snail_move_counter + 1) >= self.snail_speed
            snail_next = "🐌 WILL move" if moves_next else "🐌 resting"
            print(f"Snail: {speed_text} | {snail_next}")
        
        # Draw map
        for y in range(self.height):
            row = ""
            for x in range(self.width):
                if x == self.player_x and y == self.player_y:
                    if self.game_over:
                        row += "💀"
                    else:
                        row += avatar
                elif self.snail_active and x == self.snail_x and y == self.snail_y:
                    row += "🐌"
                elif self.fire_map[y][x]:
                    row += "🔥"
                elif self.world[y][x] == 1:
                    row += "🧱"
                elif self.world[y][x] == 2:
                    row += "💎"
                elif self.world[y][x] == 3:
                    row += "👾"
                elif self.world[y][x] == 4:
                    row += "🚪"
                else:
                    row += "⬛"
            print(row)
        
        print("-" * 30)
        print(f"💎 {self.treasure_found}/{self.total_treasures} | 👣 {self.steps_taken}")
        print(f"🏆 Total Wins: {self.stats['total_wins']}")
        print(f"⬆️  Next Evolution: {self.next_evolution()}")
        print(f"💬 {self.message}")
        self.draw_radar(avatar)
        print("\nW/A/S/D move | Q quit")
    
    def next_evolution(self):
        """Show progress to next evolution"""
        completed = self.stats['dungeons_completed']
        
        if completed <= 2:
            return f"{3 - completed} until Learner"
        elif completed <= 7:
            return f"{8 - completed} until Chef"
        elif completed <= 12:
            return f"{13 - completed} until Firefighter"
        elif completed <= 17:
            return f"{18 - completed} until Police"
        elif completed <= 23:
            return f"{24 - completed} until Ninja"
        elif completed <= 27:
            return f"{28 - completed} until Wizard"
        elif completed <= 33:
            return f"{34 - completed} until Superhero"
        else:
            return "MAX EVOLUTION! 🏆"
    
    def draw_radar(self, avatar):
        """Draw 5x5 radar around player"""
        print("\n📡 RADAR:")
        for dy in range(-2, 3):
            row = "   "
            for dx in range(-2, 3):
                world_x = self.player_x + dx
                world_y = self.player_y + dy
                
                if dx == 0 and dy == 0:
                    row += avatar
                elif 0 <= world_x < self.width and 0 <= world_y < self.height:
                    if self.snail_active and world_x == self.snail_x and world_y == self.snail_y:
                        row += "🐌"
                    elif self.fire_map[world_y][world_x]:
                        row += "🔥"
                    elif self.world[world_y][world_x] == 1:
                        row += "🧱"
                    elif self.world[world_y][world_x] == 2:
                        row += "💎"
                    elif self.world[world_y][world_x] == 3:
                        row += "👾"
                    elif self.world[world_y][world_x] == 4:
                        row += "🚪"
                    else:
                        row += "⬛"
                else:
                    row += "❌"
            print(row)
    
    def move(self, dx, dy):
        """Move player - checks what WILL happen next turn, not current state"""
        if self.game_over:
            return
        
        new_x = self.player_x + dx
        new_y = self.player_y + dy
        
        # Immediate checks (walls, boundaries, monsters)
        if new_x < 0 or new_x >= self.width or new_y < 0 or new_y >= self.height:
            self.message = "Edge of world!"
            return
        
        if self.world[new_y][new_x] == 1:
            self.message = "Thump! Wall"
            return
        
        if self.world[new_y][new_x] == 3:
            self.message = "👾 Can't move onto monster!"
            return
        
        # Check FUTURE state (next turn)
        next_fire_map = self.get_next_fire_map()
        next_snail_x, next_snail_y = self.get_next_snail_position()
        
        # Will the destination be on fire NEXT turn?
        if next_fire_map[new_y][new_x]:
            self.game_over = True
            self.death_cause = 'fire'
            self.death_message = "💀 You moved into a space that will be on fire! 💀"
            return
        
        # Will the snail be at the destination NEXT turn?
        if self.snail_active and new_x == next_snail_x and new_y == next_snail_y:
            self.game_over = True
            self.death_cause = 'snail'
            self.death_message = "🐌 You moved into a space the snail will occupy! 🐌"
            return
        
        # Check if current position will be dangerous after moving?
        # (This handles the "standing still" case - but we're moving, so it's fine)
        
        # Check if destination has treasure (these are collected immediately)
        tile = self.world[new_y][new_x]
        
        # Update position
        self.player_x, self.player_y = new_x, new_y
        
        # Handle tile effects (treasure, exit)
        if tile == 2:
            self.treasure_found += 1
            self.message = f"💎 Found treasure! ({self.treasure_found}/{self.total_treasures})"
            self.world[new_y][new_x] = 0
        
        elif tile == 4:
            if self.treasure_found == self.total_treasures:
                self.message = "🎉 DUNGEON COMPLETE! 🎉"
                self.running = False
                return
            else:
                self.message = f"🚪 Need {self.total_treasures - self.treasure_found} more!"
                # Can't exit yet, but player still moves
        
        # Advance time to next turn
        self.advance_turn()
        
        # After advancing, check if current position is now dangerous
        # (This handles the case where you move onto a tile that becomes dangerous
        # later, but you've already moved past it)
        
        # Check if snail caught you after moving
        if self.snail_active and self.player_x == self.snail_x and self.player_y == self.snail_y:
            self.game_over = True
            self.death_cause = 'snail'
            self.death_message = "🐌 The snail caught you! 🐌"
    
    def run(self):
        """Main game loop for a single dungeon"""
        while self.running and not self.game_over:
            self.draw()
            
            cmd = input("\n> ").strip().upper()
            
            if cmd == 'Q':
                self.message = "Quitting dungeon..."
                self.running = False
            elif cmd == 'W':
                self.move(0, -1)
            elif cmd == 'S':
                self.move(0, 1)
            elif cmd == 'A':
                self.move(-1, 0)
            elif cmd == 'D':
                self.move(1, 0)
            else:
                self.message = "Use W,A,S,D or Q"
            
            time.sleep(0.1)
        
        if self.game_over:
            self.simple_clear()
            print("=" * 50)
            print(self.death_message)
            print("=" * 50)
            print("\nYour adventure ends here...")
            time.sleep(2)

class StatsManager:
    """Handle saving/loading game statistics"""
    
    def __init__(self, filename="dungeon_stats.json"):
        self.filename = filename
        self.stats = self.load_stats()
    
    def load_stats(self):
        """Load stats from JSON file"""
        default_stats = {
            "total_wins": 0,
            "dungeons_completed": 0,
            "total_steps": 0,
            "total_treasures": 0,
            "snail_deaths": 0,
            "fire_deaths": 0,
            "best_dungeon": {
                "steps": float('inf'),
                "treasures": 0
            },
            "win_streak": 0,
            "last_played": None
        }
        
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    loaded = json.load(f)
                    for key, value in default_stats.items():
                        if key not in loaded:
                            loaded[key] = value
                    return loaded
            except:
                return default_stats
        return default_stats
    
    def save_stats(self):
        """Save stats to JSON file"""
        try:
            with open(self.filename, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except:
            print("⚠️  Could not save stats")
    
    # In StatsManager.update_after_dungeon() method:

    def update_after_dungeon(self, steps, treasures, won, death_cause=None):
        """Update stats after completing a dungeon"""
        old_completed = self.stats["dungeons_completed"]
        
        # ONLY increment dungeons_completed if the dungeon was WON
        # Deaths and quits should NOT count toward evolution
        if won:
            self.stats["dungeons_completed"] += 1
        
        self.stats["total_steps"] += steps
        self.stats["total_treasures"] += treasures
        self.stats["last_played"] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        if death_cause == 'snail':
            self.stats["snail_deaths"] += 1
        elif death_cause == 'fire':
            self.stats["fire_deaths"] += 1
        
        # Check if avatar evolved (only possible if won)
        if won:
            new_completed = self.stats["dungeons_completed"]
            old_avatar = self.get_avatar_name(old_completed)
            new_avatar = self.get_avatar_name(new_completed)
            
            if old_avatar != new_avatar:
                print(f"\n🌟 CONGRATULATIONS! 🌟")
                print(f"You evolved from {old_avatar} to {new_avatar}!")
                time.sleep(2)
        
        if won:
            self.stats["total_wins"] += 1
            self.stats["win_streak"] += 1
            
            if steps < self.stats["best_dungeon"]["steps"]:
                self.stats["best_dungeon"]["steps"] = steps
                self.stats["best_dungeon"]["treasures"] = treasures
        else:
            self.stats["win_streak"] = 0
        
        self.save_stats()
    
    def get_avatar_name(self, completed=None):
        """Return avatar name for a given completion count"""
        if completed is None:
            completed = self.stats['dungeons_completed']
        
        if completed <= 2:
            return "Indistinct Goon"
        elif completed <= 7:
            return "Learner"
        elif completed <= 12:
            return "Chef"
        elif completed <= 17:
            return "Firefighter"
        elif completed <= 23:
            return "Police Officer"
        elif completed <= 27:
            return "Ninja"
        elif completed <= 33:
            return "Wizard"
        else:
            return "Superhero"
    
    def display_stats(self):
        """Show career statistics"""
        avatar = self.get_avatar_name()
        
        print("\n" + "=" * 50)
        print("📊 CAREER STATISTICS")
        print("=" * 50)
        print(f"👤 Current Avatar: {avatar}")
        print(f"🏆 Total Wins: {self.stats['total_wins']}")
        print(f"📈 Dungeons Attempted: {self.stats['dungeons_completed']}")
        print(f"🔥 Current Win Streak: {self.stats['win_streak']}")
        print(f"👣 Total Steps: {self.stats['total_steps']}")
        print(f"💎 Total Treasures: {self.stats['total_treasures']}")
        print(f"🔥 Fire Deaths: {self.stats.get('fire_deaths', 0)}")
        print(f"🐌 Snail Deaths: {self.stats.get('snail_deaths', 0)}")
        
        if self.stats['best_dungeon']['steps'] != float('inf'):
            print("\n⭐ Best Run:")
            print(f"   Steps: {self.stats['best_dungeon']['steps']}")
            print(f"   Treasures: {self.stats['best_dungeon']['treasures']}")
        
        # Show evolution progress
        completed = self.stats['dungeons_completed']
        if completed <= 33:
            if completed <= 2:
                next_at = 3
                next_name = "Learner"
            elif completed <= 7:
                next_at = 8
                next_name = "Chef"
            elif completed <= 12:
                next_at = 13
                next_name = "Firefighter"
            elif completed <= 17:
                next_at = 18
                next_name = "Police Officer"
            elif completed <= 23:
                next_at = 24
                next_name = "Ninja"
            elif completed <= 27:
                next_at = 28
                next_name = "Wizard"
            else:
                next_at = 34
                next_name = "Superhero"
            
            print(f"\n⬆️  Next Evolution: {next_name} at {next_at} dungeons")
            print(f"   ({next_at - completed} more to go!)")
        else:
            print("\n🏆 MAX EVOLUTION REACHED!")
        
        if self.stats['last_played']:
            print(f"\n🕐 Last Played: {self.stats['last_played']}")
        print("=" * 50)

def show_menu():
    """Display main menu"""
    print("\n" + "=" * 50)
    print("     ⏱️  TIME-BASED DUNGEON CRAWLER ⏱️")
    print("=" * 50)
    print("1. 🎲 New Dungeon")
    print("2. 📊 View Statistics")
    print("3. ❓ How to Play")
    print("4. 🚪 Exit")
    print("=" * 50)

def show_instructions():
    """Display game instructions"""
    print("\n" + "=" * 50)
    print("📖 HOW TO PLAY")
    print("=" * 50)
    print("🎯 Objective:")
    print("   • Collect all 💎 treasures")
    print("   • Find the 🚪 exit to escape")
    print("\n⏱️  TIME-BASED MOVEMENT:")
    print("   • When you move, time advances ONE turn")
    print("   • You must predict where fire/snail WILL be")
    print("   • Current fire = 🔥, Next fire = check prediction")
    print("\n🔥 FIREBALL MONSTERS:")
    print("   • 👾 Monsters shoot fire in all 4 directions")
    print("   • Fire cycles: 3 turns ON, 3 turns OFF")
    print("   • Check NEXT turn's fire before moving!")
    print("\n🐌 STALKER SNAIL:")
    print("   • Appears at dungeon level 7")
    print("   • Speed increases every 5 levels")
    print("   • Check where snail WILL be next turn!")
    print("\n🎮 Controls: W/A/S/D move | Q quit")
    print("=" * 50)

def play_dungeon(stats_manager):
    """Play a single dungeon"""
    game = RandomDungeon(stats_manager)
    game.run()
    
    if game.game_over:
        won = False
        death_cause = game.death_cause
    else:
        won = (game.treasure_found == game.total_treasures)
        death_cause = None
    
    stats_manager.update_after_dungeon(
        game.steps_taken, 
        game.treasure_found, 
        won,
        death_cause
    )
    
    return won, death_cause

def main():
    """Main game loop"""
    stats_manager = StatsManager()
    
    while True:
        show_menu()
        choice = input("Choose an option (1-4): ").strip()
        
        if choice == "1":
            won, death_cause = play_dungeon(stats_manager)
            
            print("\n" + "=" * 50)
            if won:
                print("🎉 DUNGEON COMPLETE! 🎉")
            elif death_cause == 'snail':
                print("🐌 You were caught by the snail! 🐌")
            elif death_cause == 'fire':
                print("🔥 You were burned! 🔥")
            else:
                print("🏳️ Dungeon abandoned...")
            
            print("\nWhat would you like to do?")
            print("1. 🎲 Play Another Dungeon")
            print("2. 📊 View Stats")
            print("3. 🚪 Main Menu")
            
            while True:
                post_choice = input("\n> ").strip()
                if post_choice == "1":
                    won, death_cause = play_dungeon(stats_manager)
                    print("\n" + "=" * 50)
                    if won:
                        print("🎉 DUNGEON COMPLETE! 🎉")
                    elif death_cause == 'snail':
                        print("🐌 You were caught by the snail! 🐌")
                    elif death_cause == 'fire':
                        print("🔥 You were burned! 🔥")
                    else:
                        print("🏳️ Dungeon abandoned...")
                elif post_choice == "2":
                    stats_manager.display_stats()
                    input("\nPress Enter to continue...")
                    break
                elif post_choice == "3":
                    break
                else:
                    print("Invalid choice. Use 1, 2, or 3")
        
        elif choice == "2":
            stats_manager.display_stats()
            input("\nPress Enter to continue...")
        
        elif choice == "3":
            show_instructions()
            input("\nPress Enter to continue...")
        
        elif choice == "4":
            print("\nThanks for playing!")
            print(f"Final Stats: {stats_manager.stats['total_wins']} wins")
            stats_manager.save_stats()
            break
        
        else:
            print("Invalid choice. Please enter 1-4")

if __name__ == "__main__":
    main()
