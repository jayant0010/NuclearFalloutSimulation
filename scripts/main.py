import os
import sys
import datetime
import matplotlib
import numpy as np
import matplotlib.cm as cm
import matplotlib.pyplot as plt
from scripts.getData import getData
from matplotlib.animation import FuncAnimation, PillowWriter
from scripts.models import Rectangle, WindModel, PlumeModel

DEFAULT_SEED = 20181108


def set_up_figure(fig_size=(10, 5)):
    img = plt.imread("static\images\map.png")
    fig, ax = plt.subplots(1, 1, figsize=fig_size)

    ax.imshow(img, extent=[0, 100, -25, 25])
    title = ax.set_title('')
    return fig, ax, title


def update_decorator(dt, title, steps_per_frame, models):
    def inner_decorator(update_function):
        def wrapped_update(i):
            for j in range(steps_per_frame):
                for model in models:
                    model.update(dt)

            t = i * steps_per_frame * dt
            title.set_text('')

            return [title] + update_function(i)
        return wrapped_update
    return inner_decorator


def simulate_plume_model(dt=0.03, t_max=240, steps_per_frame=20,
                         seed=DEFAULT_SEED, latLng='21.238611,73.350000', start_datetimeObject=datetime.datetime(2020, 1, 15)):
    now = datetime.datetime.now()

    apiList, location = getData(latLng, start_datetimeObject)

    new = datetime.datetime.now()

    print("\n\n\n\n\nTIME for getdata:", (new-now), "\n\n\n\n\n")

    array = []
    speedArray = []
    dateArray = []

    for i in apiList:
        array.append(int(i['Direction']))
        speedArray.append(int(float(i['Speed'])))

        d = datetime.datetime.strptime(i['Date'], '%Y-%m-%d')
        dateArray.append(d.strftime('%b %d,%Y'))

    print("Wind Direction:", array, "\n\nWind Speed:", speedArray, "\n")

    maxElement = max(speedArray)
    speedArray = [(2*i)/maxElement for i in speedArray]

    rng = np.random.RandomState(seed)

    sim_region = Rectangle(x_min=0., x_max=100, y_min=-25., y_max=25.)

    wind_model = WindModel(
        sim_region, 21, 11, rng=rng, DirArray=array, SpdArray=speedArray, dateArray=dateArray)

    plume_model = PlumeModel(
        sim_region, wind_model=wind_model, rng=rng)

    fig, ax, title = set_up_figure()

    # Width = 0.03 to show arrows
    # Width = 0.000000000001 to hide arrows
    vf_plot = plt.quiver(
        wind_model.x_points, wind_model.y_points,
        wind_model.velocity_field.T[0], wind_model.velocity_field.T[1],
        width=0.000000000001)

    ax.axis(ax.axis() + np.array([-0.25, 0.25, -0.25, 0.25]))
    radius_mult = 200

    pp_plot = plt.scatter(
        plume_model.particle_array[:, 0], plume_model.particle_array[:, 1],
        radius_mult * plume_model.particle_array[:, 3]**0.5, c='r',
        edgecolors='none')

    ax.set_xlabel('x-coordinate / m')
    ax.set_ylabel('y-coordinate / m')

    dayText = ax.text(80, 22, "DateTime")

    ax.set_aspect(1)

    fig.tight_layout()

    @update_decorator(dt, title, steps_per_frame, [wind_model, plume_model])
    def update(i):
        vf_plot.set_UVC(wind_model.velocity_field[:, :, 0].T,
                        wind_model.velocity_field[:, :, 1].T)

        pp_plot.set_offsets(plume_model.particle_array[:, :2])
        pp_plot._sizes = radius_mult * plume_model.particle_array[:, 3]**0.5

        dayText.set_text(wind_model.day)

        if(wind_model.counter > len(wind_model.newAngleArray)):
            anim.event_source.stop()

        percentage = min(
            round((100*wind_model.counter/len(wind_model.newAngleArray)), 1), 100.0)

        print("Loading: "+str(percentage)+"%")

        return [vf_plot, pp_plot, dayText]

    n_frame = int(t_max / (dt * steps_per_frame) + 0.5)

    anim = FuncAnimation(fig, update, frames=n_frame, blit=True)
    anim.save("simulation.gif", PillowWriter(fps=15, bitrate=1800))

    print("\nConverting simulation.gif to simulation.mp4...\n")

    os.system(
        "ffmpeg -i simulation.gif ./static/videos/simulation.mp4 -loglevel quiet")

    print("\nDeleting simulation.gif...\n")

    os.remove("simulation.gif")

    new = datetime.datetime.now()
    print("\n\n\n\n\nTIME:", (new-now), "\n\n\n\n\n")

    return fig, ax, anim
