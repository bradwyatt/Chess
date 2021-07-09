# Chess

## Instructions
### File Structure
Chess.py --> Execute this file to play
initvar.py --> Review this file and check if EXE_MODE = False and TEST_MODE = False
Create a "logs" folder

### Workflow

## Maintenance
### Code Improvements (detail)
Global variables for log at the top  
In GameController.switch_turn, the "for grid in board.Grid.grid_list" logic could be in GridController  
In GameController.__del__, at the end where it references menu_buttons, instead we could create PanelController and include those lines  
json_edits.py in the /Test/ folder to use rather than .lvl  
GameController.refresh_objects might want to combine with another method somewhere, might be redundant  
Shorten arguments for functions by if I can not require it (for example, def f(piece, color) could just be f(piece) with color = piece.color)  
The functions for SwitchModesController could be a lot shorter by creating methods on other classes (then referencing those).  

### Clean Code (short-term):
Documentation  
Lint each file  
Parameterize text variables (or clean it up perhaps not include the text font name in the variable)  
Import packages and remove wild card in each files  
How to organize test functions and prints and logs (separate from production)? Removing test comments  
iCCP errors (has to do with the way it was saved on photoshop)  
Combining classes or removing certain classes. And should there be helper functions outside of classes?  
(If possible) how to shorten number of arguments for functions  

### Clean Code (long-term):
EditModeController to handle all the clicking event functions  
Panel classes in separate file (instead of menu_buttons)?  
Shorter naming conventions  
Re-examine sprite groups?  
Feedback  

### Design improvements:
If a piece moves one square, the two squares looks like a two piece in a row blob. Should the square have an outline?  
Reset Board and Clear Board, clearly distinguish the buttons?  
Black pieces to be lighter color?  

### Features To-Do (long-term):
Save positions as a .json rather than .lvl  
AI (save and load states)  
Customized Turns for black and white  
Choose piece for Promotion  
Sounds  
If no king then don't start game  
Themes  
Grid using color rather than sprite  
AI or human on BOTH sides  
