# Physical Prediction as a Decision-Making Task Over Algorithms, webppl implementation

Written by Geronimo Mirano for 6.804J Computational Cognitive Science at MIT.

Ball Physics prediction model Employing a POMDP over computations.
This is a proof-of-concept model in which an agent is trying to
predict where a ball will strike in a world. The agent is given
access to two tools: an algorithm which stochastically simulates
many balls moving forward (but which takes time to do so), and
an algorithm which uses a flood-fill approach to determine whether
it is even connected to both of the goal regions (if not, then
it knows it will eventually strike the other goal first). The
agent may only use one of the two algorithms at once, and it
uses a POMDP to decide which to carry out on each timestep.

Currently the code is rather monolithic. Run it using the webppl
framework: https://github.com/probmods/webppl/

also requires the webppl-viz and webppl-json packages:

* https://github.com/probmods/webppl-viz
* https://github.com/stuhlmueller/webppl-json

Python 2.7 is required to run the GUI in viz.py.

All code was run on Ubuntu 14.04 LTS 64-bit.
