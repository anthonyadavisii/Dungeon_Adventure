# dungeon_adventure.py
import time
import random

class Game:
    def __init__(self):
        self.player_health = 100
        self.player_inventory = []
        self.has_torch = False
        self.has_sword = False
        self.gold_coins = 0
        self.rooms_explored = 0
        
    def slow_print(self, text, delay=0.03):
        """Print text with a typing effect"""
        for char in text:
            print(char, end='', flush=True)
            time.sleep(delay)
        print()
    
    def typewriter(self, text):
        """Quick typing effect for important text"""
        self.slow_print(text, 0.02)
    
    def clear_screen(self):
        """Clear the console (works in PyCode)"""
        print("\n" * 2)
        print("=" * 60)
        print()
    
    def show_status(self):
        """Display player status"""
        print("\n" + "-" * 40)
        print(f"❤️  Health: {self.player_health}")
        print(f"💰 Gold: {self.gold_coins}")
        print(f"🎒 Items: {', '.join(self.player_inventory) if self.player_inventory else 'None'}")
        print(f"🗺️  Rooms explored: {self.rooms_explored}")
        print("-" * 40)
    
    def game_over(self, message):
        """Handle game over"""
        self.clear_screen()
        self.typewriter("☠️  " + message + " ☠️")
        self.typewriter("\nYour adventure has come to an end...")
        self.typewriter(f"\nYou explored {self.rooms_explored} rooms and found {self.gold_coins} gold.")
        return False
    
    def entrance(self):
        """Starting room"""
        self.clear_screen()
        self.typewriter("🏰 MYSTERIOUS DUNGEON")
        self.typewriter("====================")
        self.typewriter("\nYou wake up in a cold, dark dungeon.")
        self.typewriter("The last thing you remember is exploring an ancient castle.")
        self.typewriter("Now you're here, with no memory of how you arrived.")
        
        print("\nWhat do you do?")
        print("1. Look around the room")
        print("2. Try the door")
        print("3. Check your pockets")
        
        choice = input("\n> ").strip()
        
        if choice == "1":
            self.typewriter("\nYou feel around in the darkness...")
            self.typewriter("Your hands touch something metal on the floor.")
            if "Torch" not in self.player_inventory:
                self.player_inventory.append("Torch")
                self.has_torch = True
                self.typewriter("You found a TORCH! Too bad you have no way to light it...")
            return "main_hall"
            
        elif choice == "2":
            self.typewriter("\nYou try the heavy wooden door.")
            self.typewriter("It's locked tight. You'll need to find a key.")
            return "entrance"
            
        elif choice == "3":
            self.typewriter("\nYou check your pockets and find:")
            self.typewriter("- A rusty key (looks important)")
            self.typewriter("- 5 gold coins")
            if "Rusty Key" not in self.player_inventory:
                self.player_inventory.append("Rusty Key")
                self.gold_coins += 5
            return "entrance"
        
        return "entrance"
    
    def main_hall(self):
        """Main hall of the dungeon"""
        self.rooms_explored += 1
        self.clear_screen()
        self.typewriter("🏛️  MAIN HALL")
        self.typewriter("=============")
        self.typewriter("\nYou enter a large hall with high ceilings.")
        self.typewriter("Torches flicker on the walls, casting dancing shadows.")
        self.typewriter("You see three passages:")
        
        print("\nWhere do you go?")
        print("1. Left passage (you hear dripping water)")
        print("2. Right passage (a cold wind blows from here)")
        print("3. Straight ahead (a grand staircase leads up)")
        print("4. Return to entrance")
        
        choice = input("\n> ").strip()
        
        if choice == "1":
            return "water_room"
        elif choice == "2":
            return "windy_passage"
        elif choice == "3":
            if "Sword" not in self.player_inventory:
                self.typewriter("\nBefore you can go up the stairs, a skeleton warrior blocks your path!")
                return "skeleton_fight"
            return "treasure_room"
        elif choice == "4":
            return "entrance"
        
        return "main_hall"
    
    def water_room(self):
        """Room with water"""
        self.rooms_explored += 1
        self.clear_screen()
        self.typewriter("💧 WATER ROOM")
        self.typewriter("=============")
        self.typewriter("\nThe passage opens into a chamber with a underground lake.")
        self.typewriter("The water is crystal clear, and you can see something glimmering at the bottom.")
        
        print("\nWhat do you do?")
        print("1. Dive in to investigate")
        print("2. Try to fish out the object with something")
        print("3. Leave this room")
        
        choice = input("\n> ").strip()
        
        if choice == "1":
            self.typewriter("\nYou dive into the freezing water!")
            self.typewriter("You grab the glimmering object and swim back up.")
            self.typewriter("It's a GOLDEN CROWN worth 50 gold!")
            self.gold_coins += 50
            self.player_health -= 10  # Cold water damage
            self.typewriter(f"Health: {self.player_health} (lost 10 from cold)")
            if self.player_health <= 0:
                return self.game_over("You died from hypothermia!")
            
        elif choice == "2":
            if "Torch" in self.player_inventory:
                self.typewriter("\nYou use your torch to carefully fish out the object.")
                self.typewriter("It's a GOLDEN CROWN worth 50 gold!")
                self.gold_coins += 50
            else:
                self.typewriter("\nYou have nothing to fish with. The object remains out of reach.")
        
        input("\nPress Enter to continue...")
        return "main_hall"
    
    def windy_passage(self):
        """Windy passage with puzzle"""
        self.rooms_explored += 1
        self.clear_screen()
        self.typewriter("🌬️  WINDY PASSAGE")
        self.typewriter("================")
        self.typewriter("\nThe wind howls through this narrow passage.")
        self.typewriter("On the wall, you see ancient writing:")
        self.typewriter('"I speak without a mouth and hear without ears. I have no body, but I come alive with wind."')
        
        print("\nWhat is the answer?")
        print("1. Echo")
        print("2. Wind")
        print("3. Sound")
        print("4. Leave")
        
        choice = input("\n> ").strip()
        
        if choice == "1" or choice.lower() == "echo":
            self.typewriter("\nA secret door slides open!")
            self.typewriter("Behind it, you find a SWORD!")
            if "Sword" not in self.player_inventory:
                self.player_inventory.append("Sword")
                self.has_sword = True
            self.gold_coins += 20
            input("\nPress Enter to continue...")
            return "main_hall"
        elif choice in ["2", "3", "4"]:
            self.typewriter("\nNothing happens. The wind continues to howl.")
            input("\nPress Enter to continue...")
        
        return "main_hall"
    
    def skeleton_fight(self):
        """Fight with skeleton"""
        self.clear_screen()
        self.typewriter("💀 SKELETON WARRIOR")
        self.typewriter("==================")
        self.typewriter("\nA skeleton warrior blocks your path!")
        
        print("\nHow do you fight?")
        print("1. Use your bare hands")
        print("2. Look for a weapon")
        print("3. Try to run past")
        
        choice = input("\n> ").strip()
        
        if choice == "2":
            if "Sword" in self.player_inventory:
                self.typewriter("\nYou draw your sword!")
                self.typewriter("After a intense battle, you defeat the skeleton!")
                self.player_health -= 20
                self.gold_coins += 30
                self.typewriter(f"Health: {self.player_health} (lost 20 in battle)")
                if self.player_health <= 0:
                    return self.game_over("You were defeated by the skeleton!")
                self.player_inventory.append("Skeleton Key")
                self.typewriter("You found a SKELETON KEY on its remains!")
                input("\nPress Enter to continue...")
                return "treasure_room"
        elif choice == "1":
            self.typewriter("\nYou try to fight with your bare hands...")
            self.typewriter("The skeleton's sword cuts deep!")
            self.player_health -= 50
            self.typewriter(f"Health: {self.player_health}")
            if self.player_health <= 0:
                return self.game_over("The skeleton was too strong!")
        elif choice == "3":
            self.typewriter("\nYou try to run past, but the skeleton blocks you!")
            self.typewriter("It slashes your arm!")
            self.player_health -= 30
            self.typewriter(f"Health: {self.player_health}")
            if self.player_health <= 0:
                return self.game_over("You didn't make it!")
        
        return "main_hall"
    
    def treasure_room(self):
        """Final treasure room"""
        self.rooms_explored += 1
        self.clear_screen()
        self.typewriter("✨ TREASURE ROOM")
        self.typewriter("================")
        self.typewriter("\nYou enter a magnificent chamber filled with treasure!")
        self.typewriter("Gold coins, jewels, and ancient artifacts fill the room.")
        
        total_gold = 100 + self.gold_coins
        
        self.typewriter(f"\nYou've found a fortune! Total gold: {total_gold}")
        self.typewriter(f"Rooms explored: {self.rooms_explored}")
        self.typewriter(f"Items collected: {len(self.player_inventory)}")
        
        print("\n🎉 CONGRATULATIONS! YOU WIN! 🎉")
        print("\nWhat would you like to do?")
        print("1. Play again")
        print("2. Quit")
        
        choice = input("\n> ").strip()
        
        if choice == "1":
            return "restart"
        else:
            self.typewriter("\nThanks for playing!")
            return "quit"
    
    def run(self):
        """Main game loop"""
        current_room = "entrance"
        
        while True:
            self.show_status()
            
            if current_room == "entrance":
                current_room = self.entrance()
            elif current_room == "main_hall":
                current_room = self.main_hall()
            elif current_room == "water_room":
                current_room = self.water_room()
            elif current_room == "windy_passage":
                current_room = self.windy_passage()
            elif current_room == "skeleton_fight":
                current_room = self.skeleton_fight()
            elif current_room == "treasure_room":
                current_room = self.treasure_room()
                if current_room == "restart":
                    # Reset game
                    self.__init__()
                    current_room = "entrance"
                elif current_room == "quit":
                    break
            elif isinstance(current_room, bool) and not current_room:
                # Game over occurred
                break
            else:
                # Invalid room, go back to entrance
                current_room = "entrance"

if __name__ == "__main__":
    game = Game()
    game.run()
    
    print("\n" + "=" * 60)
    print("Thanks for playing Mysterious Dungeon!")
    print("Created with PyCode on Samsung S24 Ultra")
    print("=" * 60)
