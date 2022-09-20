# Shelyak frontend
 
### Python web app for the Sheylak spectrograph 

This is a Python web app for the shelyak spectorgraph written in ``Python/Dash``. Eventually this system will be used to control the shelyak spectrograph. It should interface with a server running behind the scences using ``socket.io``. 

Requirements for the GUI
- Choose an observing type from ``Dark``, ``Flat``, ``Wavelength Calibration``, ``Object``. The first three are calibrations that only need the spectrograph, ``Object`` is an actual observation.
- Resolve a target using [Simbad/astroquery](https://astroquery.readthedocs.io/en/latest/simbad/simbad.html) to get the target position on the sky (RA/Dec) and if the target is observable (``secz < 4``).