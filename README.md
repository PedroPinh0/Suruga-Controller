<!-- ABOUT THE PROJECT -->
## About The Project

This project was born out of the frustration of using a Python raw code as a controller for a stepper motor I have in my Photonics lab. So I decided to create a GUI to make my life easier.

As you will see when you run the .py file: This is a simple controller, not meant to be pretty, but useful. I have separated the controllers for the Z axis from the XY plane to decrease the need to keep changing the step size each time you move in the XY plane since the steps taken in the Z axis are usually smaller than the one taken in the XY plane.

The XY controllers and Z controllers are identical. On the left side you have the direction controllers and a CLEAR button (to erase the step size), on the right side you can choose the step size and the unit (millimeters or microns).

There is also a Net Z distance traveled logger in the bottom of the window.

This is open project so do what you want with this code. This code clearly isn't a masterpiece in terms of organization and definetly not Pythonic enough. Feel free to fork it and make it better.


![example](https://github.com/PedroPinh0/Suruga-Controller/blob/master/example.png?raw=true)

<!-- CONTACT -->
## Contact

Pedro Pinho - ppinho@ifi.unicamp.br
