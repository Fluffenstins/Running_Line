from matplotlib import pyplot as plt
from math import sin, cos, tan, pi, ceil


class LineCalculator:
    def __init__(self, uom='m'):
        self.max_delta = 0
        self.delta_max = 6
        self.rod_length = 3
        self.uom = 'm'
        self.start_angle = 24
        self.min_angle = 4

        self.end_pos = None

        # calc min_radius
        if self.min_angle == 0:
            self.min_radius = float('inf')
        else:
            a = self.min_angle*pi/180
            b = (pi-a)/2
            self.min_radius = self.rod_length*sin(b)/sin(a)

        self.num_rods = 0
        self.instructions = []

        self.rods = []
        self.angles = []

    def set_uom(self, uom):
        if uom == 'm' and self.uom == 'ft':
            self.rod_length *= 0.3048
            self.uom = 'm'
        elif uom == 'ft' and self.uom == 'm':
            self.rod_length /= 0.3048
            self.uom = 'ft'

    def readable_rod_info(self, rod_pos, rads, percent=False):
        rod_pos = [round(i, 2) for i in rod_pos]

        if percent:
            angle = tan(rads)
        else:
            angle = round(rads*180/pi, 2)

        return f"({rod_pos[0]}{self.uom}, {rod_pos[1]}{self.uom}) @ {angle}"

    def reset(self):
        self.max_delta = 0
        self.num_rods = 0
        self.instructions = []
        self.rods = []
        self.angles = []

    def calc_line(self, points, angles):
        # each item in i is a 2d vector that corresponds to an item in angles
        # angles shows the desired angle at each point

        self.reset()

        ret = [points[0]]
        for n in range(1, len(points)):
            p1 = ret[-1]
            p2 = points[n]
            a1 = angles[n-1]
            a2 = angles[n]

            ret += self.subdivide(p1, p2, a1, a2, self.rod_length)
        print(f"ret {ret}")
        self.end_pos = f"End Pos: ({ret[-1][0]},{ret[-1][1]})"
        self.plot_points(ret, points)

    def subdivide(self, p1, p2, a1, a2, rod_length=3):
        angle_delta = (a2-a1)*pi/180  # Note: we now accept rads by default
        m1 = tan(a1*pi/180)  # slope 1
        m2 = tan(a2*pi/180)  # slope 2
        b1 = m1*p1[0] - p1[1]  # y offset
        b2 = m2*p2[0] - p2[1]  # y offset
        x_int = (b1-b2)/(m1-m2)  # total distance along x
        y_int = m1*x_int-b1  # total distance along 7
        d1 = round(distance(p1, [x_int, y_int]),3)
        d2 = round(distance(p2, [x_int, y_int]),3)
        r_prime = min(d1, d2)*tan((pi-angle_delta)/2)
        r = max(r_prime, self.min_radius)

        d = min(d1, d2)*r/r_prime

        # d = min(d1, d2)*sin(angle_delta)/sin((pi-angle_delta)/2)
        s = angle_delta*r  # arc length that we expect the line to curve along
        s_tot = s + max(d1, d2) - r

        ret = [p1]
        angles = [a1*pi/180]

        def move(delta):
            self.num_rods += 1
            x = ret[-1][0]
            y = ret[-1][1]
            angle = angles[-1] + delta/2
            # print(f"x:{x}, y:{y}, theta:{angle}")

            x1 = x + rod_length*cos(angle)
            y1 = y + rod_length*sin(angle)

            ret.append([x1, y1])
            angles.append(angle + delta/2)

        if d1 > d:
            for i in range(int((d1-d)//rod_length)+1):
                move(0)
            self.instructions.append([int((d1-d)//rod_length)+1, 0])

        delta = angle_delta/(s//rod_length)
        # print(f"Delta: {delta*180/pi}")
        self.max_delta = max(self.max_delta, abs(delta*180/pi))
        for i in range(int(s//rod_length)):
            move(delta)
        self.instructions.append([int(s//rod_length), delta])

        if d2 > d:
            for i in range(int(ceil((d2-d)/rod_length))):
                move(0)
            self.instructions.append([int((d2-d)//rod_length)+1, 0])

        self.rods += ret
        self.angles += angles

        print(f"instructions {ret}")

        return ret

    @staticmethod
    def plot_points(points, dots=None, show=False):
        x = [i for i, j in points]
        y = [j for i, j in points]

        plt.plot(x, y)

        if dots is not None:
            x = [i for i, j in dots]
            y = [j for i, j in dots]
            plt.scatter(x, y, s=10, c='orange')

        if show:
            plt.show()
        return plt


def distance(p1, p2):
    return sum([(i-j)**2 for i, j in zip(p1, p2)])**0.5


def bend_radius_to_angle(radius, rod_length=3, rads=True):
    alpha = rod_length/radius
    if rads:
        return alpha
    else:
        return alpha*180/pi


if __name__ == "__main__":
    print(bend_radius_to_angle(25, 3, False))
    LineCalculator().calc_line([[0,0], [20, -5], [70, 0]], [-25, 0, 25])
