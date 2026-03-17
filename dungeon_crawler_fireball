# dungeon_crawler_fireball.py
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
        self.message = "Welcome to RANDOM dungeon! Watch out for FIRE!"
        self.steps_taken = 0
        self.treasure_found = 0
        self.game_over = False
        self.death_message = ""
        
        # Fire cycle tracking
        self.fire_cycle = 0  # 0-5: 0-2 = fire ON, 3-5 = fire OFF
        self.fire_timer = 0
        
        self.width = 12
        self.height = 12
        
        self.world = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.fire_map = [[False for _ in range(self.width)] for _ in range(self.height)]
        self.monster_positions = []  # Track where monsters are
        self.generate_dungeon()
    
    def get_avatar(self):
        """Return the appropriate avatar based on dungeons completed"""
        completed = self.stats['dungeons_completed']
        
        if completed <= 2:
            return "👤"      # 0-2: Indistinct Goon
        elif completed <= 7:
            return "👨‍🎓"    # 3-7: Learner
        elif completed <= 12:
            return "👩‍🍳"    # 8-12: Chef
        elif completed <= 17:
            return "👨‍🚒"    # 13-17: Firefighter
        elif completed <= 23:
            return "👮‍♂️"    # 18-23: Police Officer
        elif completed <= 27:
            return "🥷"      # 24-27: Ninja
        elif completed <= 33:
            return "🧙‍♂️"    # 28-33: Wizard
        else:
            return "🦸‍♂️"    # 34+: Superhero
    
    def get_avatar_name(self):
        """Return the name of current avatar"""
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
                    self.world[y][x] = 3  # Monster
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
    
    def update_fire(self):
        """Update fire state based on cycle"""
        self.fire_cycle = (self.fire_cycle + 1) % 6
        fire_active = (self.fire_cycle < 3)  # First 3 turns ON, next 3 OFF
        
        # Clear previous fire
        for y in range(self.height):
            for x in range(self.width):
                self.fire_map[y][x] = False
        
        if fire_active:
            # Create fire around each monster
            for mx, my in self.monster_positions:
                # Fire in all 4 directions
                directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
                for dx, dy in directions:
                    fx, fy = mx + dx, my + dy
                    # Check bounds and not a wall
                    if (0 <= fx < self.width and 0 <= fy < self.height and 
                        self.world[fy][fx] != 1):
                        self.fire_map[fy][fx] = True
            
            # Check if player is in fire
            if self.fire_map[self.player_y][self.player_x]:
                self.game_over = True
                self.death_message = "💀 You were consumed by fire! 💀"
    
    def draw(self):
        """Draw the game with fire effects"""
        self.simple_clear()
        
        # Update fire first
        self.update_fire()
        
        # Get current avatar
        avatar = self.get_avatar()
        avatar_name = self.get_avatar_name()
        
        print("🔥 FIREBALL DUNGEON CRAWLER 🔥")
        print(f"Dungeon #{self.stats['dungeons_completed'] + 1}")
        print(f"Avatar: {avatar} {avatar_name}")
        
        # Show fire status
        fire_status = "🔥 ACTIVE" if self.fire_cycle < 3 else "💨 cooling down"
        turns_left = 3 - self.fire_cycle if self.fire_cycle < 3 else 6 - self.fire_cycle
        print(f"Fire: {fire_status} ({turns_left} turns)")
        
        # Draw map
        for y in range(self.height):
            row = ""
            for x in range(self.width):
                if x == self.player_x and y == self.player_y:
                    if self.game_over:
                        row += "💀"  # Skull if dead
                    else:
                        row += avatar
                elif self.fire_map[y][x]:
                    row += "🔥"  # Fire
                elif self.world[y][x] == 1:
                    row += "🧱"  # Wall
                elif self.world[y][x] == 2:
                    row += "💎"  # Treasure
                elif self.world[y][x] == 3:
                    row += "👾"  # Monster
                elif self.world[y][x] == 4:
                    row += "🚪"  # Exit
                else:
                    row += "⬛"  # Empty
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
            return f"{3 - completed} dungeons until Learner"
        elif completed <= 7:
            return f"{8 - completed} dungeons until Chef"
        elif completed <= 12:
            return f"{13 - completed} dungeons until Firefighter"
        elif completed <= 17:
            return f"{18 - completed} dungeons until Police Officer"
        elif completed <= 23:
            return f"{24 - completed} dungeons until Ninja"
        elif completed <= 27:
            return f"{28 - completed} dungeons until Wizard"
        elif completed <= 33:
            return f"{34 - completed} dungeons until Superhero"
        else:
            return "MAX EVOLUTION REACHED! 🏆"
    
    def draw_radar(self, avatar):
        """Draw 5x5 radar around player"""
        print("\n📡 RADAR:")
        for dy in range(-2, 3):
            row = "   "
            for dx in range(-2, 3):
                world_x = self.player_x + dx
                world_y = self.player_y + dy
                
                if dx == 0 and dy == 0:
                    if self.game_over:
                        row += "💀"
                    else:
                        row += avatar
                elif 0 <= world_x < self.width and 0 <= world_y < self.height:
                    if self.fire_map[world_y][world_x]:
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
        """Move player"""
        if self.game_over:
            return
        
        new_x = self.player_x + dx
        new_y = self.player_y + dy
        
        if new_x < 0 or new_x >= self.width or new_y < 0 or new_y >= self.height:
            self.message = "Edge of world!"
            return
        
        if self.world[new_y][new_x] == 1:
            self.message = "Thump! Wall"
            return
        
        if self.world[new_y][new_x] == 3:
            self.message = "👾 The fire creature glows hotter!"
            # Don't move onto monster
            return
        
        # Check if destination is on fire
        if self.fire_map[new_y][new_x]:
            self.game_over = True
            self.death_message = "💀 You stepped into fire and perished! 💀"
            return
        
        old_x, old_y = self.player_x, self.player_y
        self.player_x, self.player_y = new_x, new_y
        self.steps_taken += 1
        
        tile = self.world[new_y][new_x]
        
        if tile == 2:
            self.treasure_found += 1
            self.message = f"💎 Found treasure! ({self.treasure_found}/{self.total_treasures})"
            self.world[new_y][new_x] = 0
            
        elif tile == 4:
            if self.treasure_found == self.total_treasures:
                self.message = "🎉 DUNGEON COMPLETE! 🎉"
                self.running = False
            else:
                self.message = f"🚪 Need {self.total_treasures - self.treasure_found} more treasures!"
                self.player_x, self.player_y = old_x, old_y
                self.steps_taken -= 1
        else:
            self.message = "Moved"
    
    def run(self):
        """Main game loop for a single dungeon"""
        while self.running and not self.game_over:
            self.draw()
            
            # Get input
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
        
        # Show death screen if game over
        if self.game_over:
            self.simple_clear()
            print("=" * 50)
            print(self.death_message)
            print("=" * 50)
            print("\nYour adventure ends here...")
            time.sleep(2)

# [StatsManager, show_menu(), show_instructions(), play_dungeon(), main() functions remain the same]
# Include all the same supporting functions from the previous version

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
                    # Merge with defaults
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
    
    def update_after_dungeon(self, steps, treasures, won):
        """Update stats after completing a dungeon"""
        old_completed = self.stats["dungeons_completed"]
        self.stats["dungeons_completed"] += 1
        self.stats["total_steps"] += steps
        self.stats["total_treasures"] += treasures
        self.stats["last_played"] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Check if avatar evolved
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
            
            # Check if this was a best run
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
        """Show career statistics with current avatar"""
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
    print("     🔥 FIREBALL DUNGEON 🔥")
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
    print("\n🔥 NEW MECHANIC: FIREBALL MONSTERS")
    print("   • 👾 Monsters shoot fire in all 4 directions!")
    print("   • Fire cycles: 3 turns ON, 3 turns OFF")
    print("   • 🔥 Fire tiles are INSTANT DEATH")
    print("   • Watch the fire timer and plan your moves!")
    print("\n🎮 Controls:")
    print("   • W/A/S/D - Move your character")
    print("   • Q - Quit current dungeon")
    print("\n⬆️  EVOLUTION:")
    print("   • Complete dungeons to evolve your avatar!")
    print("   • 👤 → 👨‍🎓 → 👩‍🍳 → 👨‍🚒 → 👮‍♂️ → 🥷 → 🧙‍♂️ → 🦸‍♂️")
    print("=" * 50)

def play_dungeon(stats_manager):
    """Play a single dungeon"""
    game = RandomDungeon(stats_manager)
    game.run()
    
    # Check if player won or died/quitting
    if game.game_over:
        won = False
    else:
        won = (game.treasure_found == game.total_treasures)
    
    # Update stats using the manager
    stats_manager.update_after_dungeon(game.steps_taken, game.treasure_found, won)
    
    return won

def main():
    """Main game loop with menu and persistence"""
    stats_manager = StatsManager()
    
    while True:
        show_menu()
        choice = input("Choose an option (1-4): ").strip()
        
        if choice == "1":
            # Play dungeon
            won = play_dungeon(stats_manager)
            
            # Show completion dialogue
            print("\n" + "=" * 50)
            if won:
                print("🎉 DUNGEON COMPLETE! 🎉")
            else:
                print("🏳️ Dungeon failed...")
            
            print("\nWhat would you like to do?")
            print("1. 🎲 Play Another Dungeon")
            print("2. 📊 View Stats")
            print("3. 🚪 Main Menu")
            
            while True:
                post_choice = input("\n> ").strip()
                if post_choice == "1":
                    # Play again immediately
                    won = play_dungeon(stats_manager)
                    print("\n" + "=" * 50)
                    if won:
                        print("🎉 DUNGEON COMPLETE! 🎉")
                    else:
                        print("🏳️ Dungeon failed...")
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
            avatar = stats_manager.get_avatar_name()
            print(f"Final Avatar: {avatar}")
            print(f"Final Stats: {stats_manager.stats['total_wins']} wins in {stats_manager.stats['dungeons_completed']} dungeons")
            stats_manager.save_stats()
            break
        
        else:
            print("Invalid choice. Please enter 1-4")

if __name__ == "__main__":
    main()
