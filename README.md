# Booksnek

🐍 **Booksnek** is an updated Pygame implementation of PopCap's classic Flash game Bookworm.

![](./img/preview.PNG)

### Features
- Load & save gamestates
- `High score`, `longest word` and `best word` metrics
- Word history, including tile types used
- HP damage & heal mechanics replace the old "burn down the library" endgame
- "Explosive" area-effect tiles
- Quickly find tiles on the board by typing their letter
- Right click to mark tiles so you don't misplace them
- No more losing your power-up tiles on Scramble
- Word difficulty ranking system that prevents the game from choosing ridiculously rare bonus words like "PYX" and "QUIZZES"
- Letter distribution and value scales based on Scrabble
- Straightforward scoring system

### Requires
- Python 3.8.3
- Pygame 2.0.0.dev10
- Numpy 1.18.5

### TODO
- Add tutorial GIFs and documentation
- Limit to 5 saved gamestates; create menu to choose/overwrite
- SFX (and menu to control)
- Music?

### Known bugs
- Tile rows get messed up after save / reload