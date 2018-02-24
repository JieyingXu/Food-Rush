FoodRush
2017/12/07
author: Jieying XU
andrew ID: jieyingx

This is a pygame game incorporated openCV object tracking and game AI. All the character icon,
wall icons and the whole GUI are designed originally. The food icons are from google pictures.

The goal of this game is to control the movement of a hero to eat as many food as it can by keyboard
control or hand motion control using web camera capture. In the game process, each level will have
different numbers of monsters chasing dynamically after the hero with different speed.
The hero must try not to be touched by the monsters, or the count of remaining lives will decrease
by 1 and the hero and monsters will be sent back to its start position.

In the beginning of the game, the player has three lives, and with each 300 points earned,
the player can get an extra life. In each level, burgers must be all eaten and the hero must reach
the yellow leaf's position to successfully enter next level.

In the start screen, highScores section keeps record of the highest three scores and their
corresponding playing time through game history.

To run this game, you will need the following modules: pygame, opencv2(cv2), numpy and networkx.
And the python version should be python 2.X(I used Anaconda2 here for the convenience of those
pre-installed modules.) After installing all modules above, run FoodRush.py and enjoy the game.