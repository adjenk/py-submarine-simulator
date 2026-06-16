# 2D Newtonian Submarine Simulator

## Todo
- Propellors generate linear thrust relative to the whole submarine's center of mass (i.e. a propellor misaligned w/ the center of mass produces less linear thrust [torque from propellor thrust is not yet working!])
- Dynamic buoyancy via gradient water pressure (thus simulated, controllable ballast tanks allow the submarine to effect an upwards thrust)
- Simulates rigid body linear friction
- Friction causes torque to the center of mass causing rotation (i.e. one can steer the submarine by rotating its wings [assumming the propellor is applying linear thrust])
- Uses water pressure to calculate friction values
- All of the above obeys newtonian physics, e.g. Archimedes principle of buoyancy, preservation of motion, newtons second law
- add graphics
- add curved surface friction adjustment i.e. allow for aerodynamic structures like a nose cone to apply friction dampening in the calculations

## What this will NOT simulate
- particle motion or pressure due to particle motion
- water dynamics: dynamic water column heights, water height due to submarine displacement
- Elastic bodies or deformation
- anything 3D
