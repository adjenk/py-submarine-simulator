# 2D Submarine Simulator

## Todo
- Working physics loop: Submarine has mass, forces are applied each tick, velocity and position update from those forces
- Flat buoyancy (Archimedes principle)
- Propeller linear thrust via physics loop
- Rigid body linear friction / drag using water pressure
- Gradient water pressure buoyancy as extension of flat buoyancy
- Propeller torque and wing steering (requires rotational physics: moment of inertia, angular velocity)

## Stretch Goals
- Curved surface friction adjustment (aerodynamic nose cone drag dampening)

## What this will NOT simulate
- particle motion or pressure due to particle motion
- water dynamics: dynamic water column heights, water height due to submarine displacement
- Elastic bodies or deformation
- anything 3D
