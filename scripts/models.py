import math
import numpy as np
import scipy.interpolate as interp


class SlottedIterable(object):
    __slots__ = ()

    def __iter__(self):
        for name in self.__slots__:
            yield getattr(self, name)

    def __repr__(self):
        return '{cls}({attr})'.format(
            cls=self.__class__.__name__,
            attr=', '.join(['{0}={1}'.format(
                name, getattr(self, name)) for name in self.__slots__]))


class Particle(SlottedIterable):
    __slots__ = ('x', 'y', 'z', 'r_sq')

    def __init__(self, x, y, z, r_sq):
        if not(r_sq >= 0.):
            print('Error: r_sq must be non-negative.')

        self.x = x
        self.y = y
        self.z = z
        self.r_sq = r_sq


class Rectangle(SlottedIterable):
    __slots__ = ('x_min', 'x_max', 'y_min', 'y_max')

    def __init__(self, x_min, x_max, y_min, y_max):
        if not(x_min < x_max):
            print('Eror: Rectangle x_min must be < x_max.')

        if not(y_min < y_max):
            print('Error: Rectangle y_min must be < y_max.')

        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max

    @property
    def w(self):
        return self.x_max - self.x_min

    @property
    def h(self):
        return self.y_max - self.y_min

    def contains(self, x, y):
        return (x >= self.x_min and x <= self.x_max and
                y >= self.y_min and y <= self.y_max)


class PlumeModel(object):
    def __init__(self, sim_region=None, source_pos=(50., 0., 0.),
                 wind_model=None, model_z_disp=True, centre_rel_diff_scale=2.,
                 particle_init_rad=0.0316, particle_spread_rate=0.001,
                 particle_release_rate=10, init_num_particles=10, max_num_particles=1000,
                 rng=None):

        if sim_region is None:
            sim_region = Rectangle(0., 50., -12.5, 12.5)

        if rng is None:
            rng = np.random

        self.sim_region = sim_region

        if wind_model is None:
            wind_model = WindModel()

        self.wind_model = wind_model

        self.rng = rng

        self.model_z_disp = model_z_disp
        self._vel_dim = 3 if model_z_disp else 2

        if model_z_disp and hasattr(centre_rel_diff_scale, '__len__'):
            if not(len(centre_rel_diff_scale) == 2):
                print('Error: centre_rel_diff_scale must be a scalar or leng = 1 or 3')

        self.centre_rel_diff_scale = centre_rel_diff_scale

        if not(sim_region.contains(source_pos[0], source_pos[1])):
            print('Error: Specified source position must be within simulation region.')

        source_z = 0 if len(source_pos) != 3 else source_pos[2]

        self._new_particle_params = (
            source_pos[0], source_pos[1], source_z, particle_init_rad**2)

        self.particle_spread_rate = particle_spread_rate

        self.particle_release_rate = particle_release_rate

        self.max_num_particles = max_num_particles

        # Self.particles is an array containing the active particles.
        self.particles = [
            Particle(*self._new_particle_params) for i in range(init_num_particles)]

    def update(self, dt):
        if len(self.particles) < self.max_num_particles:
            num_to_release = min(
                self.rng.poisson(self.particle_release_rate * dt),
                self.max_num_particles - len(self.particles))

            self.particles += [
                Particle(*self._new_particle_params) for i in range(num_to_release)]

        alive_particles = []

        for particle in self.particles:
            wind_vel = np.zeros(self._vel_dim)
            wind_vel[:2] = self.wind_model.velocity_at_pos(
                particle.x, particle.y)

            filament_diff_vel = (self.rng.normal(size=self._vel_dim) *
                                 self.centre_rel_diff_scale)
            vel = wind_vel + filament_diff_vel

            particle.x += vel[0] * dt
            particle.y += vel[1] * dt

            if self.model_z_disp:
                particle.z += vel[2] * dt
            particle.r_sq += self.particle_spread_rate * dt

            if self.sim_region.contains(particle.x, particle.y):
                alive_particles.append(particle)
        self.particles = alive_particles

    @property
    def particle_array(self):
        return np.array([tuple(particle) for particle in self.particles])


class WindModel(object):
    def __init__(self, sim_region=None, n_x=21, n_y=21, u_av=1., v_av=0., rng=None, DirArray=[], SpdArray=[], dateArray=[]):
        if sim_region is None:
            sim_region = Rectangle(0, 100, -50, 50)

        if rng is None:
            rng = np.random

        self.sim_region = sim_region

        self.u_av = u_av
        self.v_av = v_av

        self.n_x = n_x
        self.n_y = n_y

        self.dx = sim_region.w / (n_x - 1)
        self.dy = sim_region.h / (n_y - 1)

        self._u = np.ones((n_x + 2, n_y + 2)) * u_av
        self._v = np.ones((n_x + 2, n_y + 2)) * v_av

        self._u_int = self._u[1:-1, 1:-1]
        self._v_int = self._v[1:-1, 1:-1]

        self._x_points = np.linspace(sim_region.x_min, sim_region.x_max, n_x)
        self._y_points = np.linspace(sim_region.y_min, sim_region.y_max, n_y)

        self._interp_set = True

        self.counter = 0
        self.magnitude = 1
        self.angle = 0

        self.newU = 0
        self.newV = 0

        self.day = ""

        self.angleArray = DirArray[:14]
        self.speedArray = SpdArray[:14]
        self.dateArray = dateArray[:14]

        self.newAngleArray = self.createAngleArray(self.angleArray)
        self.newSpeedArray = self.createSpeedArray(self.speedArray)
        self.newDateArray = self.createDateArray(self.dateArray)

    def _set_interpolators(self):
        self._interp_u = interp.RectBivariateSpline(
            self.x_points, self.y_points, self._u_int)

        self._interp_v = interp.RectBivariateSpline(
            self.x_points, self.y_points, self._v_int)

        self._interp_set = True

    @property
    def x_points(self):
        return self._x_points

    @property
    def y_points(self):
        return self._y_points

    @property
    def velocity_field(self):
        return np.dstack((self._u_int, self._v_int))

    def velocity_at_pos(self, x, y):
        if not self._interp_set:
            self._set_interpolators()
        return np.array([float(self._interp_u(x, y)),
                         float(self._interp_v(x, y))])

    def update(self, dt):
        try:
            self.angle = self.newAngleArray[self.counter]
            self.magnitude = self.newSpeedArray[self.counter]
            self.counter += 1
            self.day = self.newDateArray[self.counter//25]
        except IndexError:
            pass

        self.newU = self.magnitude*math.cos(self.angle * (math.pi/180))
        self.newV = self.magnitude*math.sin(self.angle * (math.pi/180))

        self.du = self.newU - self._u_int[0][0]
        self.dv = self.newV - self._v_int[0][0]

        self._u_int += self.du
        self._v_int += self.dv

        self._interp_set = False

    def createAngleArray(self, angleArray):
        for i in range(len(angleArray)):
            if angleArray[i] <= 90:
                angleArray[i] = 90 - angleArray[i]
            else:
                angleArray[i] = 450 - angleArray[i]

        for i in range(len(angleArray)-1):
            dif = abs(angleArray[i+1] - angleArray[i])

            if dif <= 30:
                if angleArray[i+1] > angleArray[i]:
                    angleArray[i+1] = (angleArray[i] + 30) % 360
                else:
                    angleArray[i+1] = angleArray[i] - 30
                    if angleArray[i+1] < 0:
                        angleArray[i+1] += 360

        tempAngleArray = []

        for i in range(len(angleArray)-1):
            tempAngleArray.append(angleArray[i])
            difference = angleArray[i+1] - angleArray[i]
            sign = np.sign(difference)
            magDiff = abs(difference)

            if magDiff > 180:
                magDiff = abs(magDiff - 360)
                sign = sign * -1

            difference = magDiff * sign
            difference = difference/600

            for j in range(1, 600):
                newAngle = angleArray[i]+difference*j
                if newAngle < 0:
                    newAngle += 360
                elif newAngle > 360:
                    newAngle -= 360
                tempAngleArray.append(newAngle)

        tempAngleArray.append(angleArray[-1])
        return tempAngleArray

    def createSpeedArray(self, speedArray):
        tempSpeedArray = []
        difference = 0

        for i in range(len(speedArray)-1):
            tempSpeedArray.append(speedArray[i])

            difference = speedArray[i+1] - speedArray[i]
            difference = difference/600

            for j in range(1, 600):
                increment = speedArray[i]+difference*j
                tempSpeedArray.append(increment)

        tempSpeedArray.append(speedArray[-1])
        return tempSpeedArray

    def createDateArray(self, dateArray):
        tempDateArray = []

        for i in range(len(dateArray)):
            tempDateArray.append(dateArray[i]+" 00:00:00")

            for j in range(1, 10):
                dateStr = dateArray[i]+" 0"+str(j)+":00:00"
                tempDateArray.append(dateStr)

            for j in range(10, 24):
                dateStr = dateArray[i]+" "+str(j)+":00:00"
                tempDateArray.append(dateStr)

        return tempDateArray
