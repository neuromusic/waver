import numpy as np
from tqdm import tqdm

from ._grid import Grid
from ._source import Source
from ._time import Time


class Simulation:
    """Simulation of wave equation for a certain time on a defined grid.

    The simulation is always assumed to start from zero wave initial
    conditions, but is driven by a source. Therefore the `add_source`
    method must be called before the simulation can be `run`.
    """
    def __init__(self, *, size, spacing, speed, duration):
        """
        Parameters
        ----------
        size : tuple of float
            Size of the grid in meters. Length of size determines the
            dimensionality of the grid.
        spacing : float
            Spacing of the grid in meters. The grid is assumed to be
            isotropic, all dimensions use the same spacing.
        speed : float or array
            Speed of the wave in meters per second. If a float then
            speed is assumed constant across the whole grid. If an
            array then must be the same shape as the shape of the grid.
        duration : float
            Length of the simulation in seconds.
        """
        self._grid = Grid(size, spacing, speed)

        # Calculate the theoretically optical courant number
        # given the dimensionality of the grid
        courant_number = float(self.grid.ndim) ** (0.5)

        # Based on the counrant number and the maximum speed
        # calculate the largest stable time step
        max_speed = np.max(self.grid.speed)
        max_step = courant_number * self.grid.spacing / max_speed

        # Round step, i.e. 5.047e-7 => 5e-7
        power =  np.power(10, np.floor(np.log10(max_step)))
        coef = int(np.floor(max_step / power))
        step = coef * power

        self._time = Time(step, duration)

        self._wave = np.zeros((self.time.nsteps,) + self.grid.shape)
        self._source = None
        self._run = False

    @property
    def grid(self):
        """Grid: Grid that simulation is defined on."""
        return self._grid

    @property
    def time(self):
        """Time: Time that simulation is defined over."""
        return self._time

    @property
    def source(self):
        """Source: Source that drives simulation."""
        if self._source is None:
            raise ValueError('Please add a source before running, use Simulation.add_source()')
        else:
            return self._source

    @property
    def wave(self):
        """array: Array for the wave."""
        if self._run:
            return self._wave
        else:
            raise ValueError('Simulation must be run first, use Simulation.run()')

    def run(self):
        """Run the simulation.
        
        Note a source must be added before the simulation can be run.
        """
        if self._source is None:
            raise ValueError('Please add a source before running, use Simulation.add_source()')

        for current_step in tqdm(range(self.time.nsteps)):
            current_time = self.time.step * current_step
            # Not this is not the actual wave equation!
            self._wave[current_step] = self.source.value(current_time)
        self._run = True

    def add_source(self, *, location, frequency, ncycles=None, phase=0,):
        """Add a source to the simulaiton.
        
        Note this must be done before the simulation can be run.

        The added source will be a sinusoid with a fixed spatial weight
        and vary either contiously or for a fixed number of cycles.

        Parameters
        ----------
        location : tuple of float or None
            Location of source in m. If None is passed at a certain location
            of the tuple then the source is broadcast along the full extent
            of that axis. For example a source of `(0.1, 0.2, 0.1)` is a
            point source in 3D at the point x=10cm, y=20cm, z=10cm. A source of
            `(0.1, None, 0.1)` is a line source in 3D at x=10cm, z=10cm extending
            the full length of y.
        frequency : float
            Frequency of the source in cycles per second.
        ncycles : int or None
            If None, source is considered to be continous, otherwise
            it will only run for ncycles.
        phase : float
            Phase offset of the source in radians.
        """
        self._run = False
        self._source = Source(
                              location=location,
                              shape=self.grid.shape,
                              spacing=self.grid.spacing,
                              frequency=frequency,
                              ncycles=ncycles,
                              phase=phase,
                             )

    def set_boundaries(boundaries):
        """Set boundary conditions
        
        Parameters
        ----------
        boundaries : list of 2-tuple of str
            For each axis, a 2-tuple of the boundary conditions where the 
            first and second values correspond to low and high boundaries
            of the axis. The acceptable boundary conditions are `PML` and
            `periodic` for Perfectly Matched Layer, and periodic conditions
            respectively.
        """
        # Not yet implemented
        pass