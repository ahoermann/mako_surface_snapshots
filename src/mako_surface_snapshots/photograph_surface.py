import sys
import argparse
from bayes_opt import BayesianOptimization, SequentialDomainReductionTransformer
from bayes_opt.acquisition import ExpectedImprovement
from epics import caput, caget


class SurfacePhotographer:
    def __init__(self, mako_prefix, motor_address, motor_min, motor_max):
        self.mako_prefix = mako_prefix
        self.motor_address = motor_address
        self.motor_min = motor_min
        self.motor_max = motor_max

    def black_box_function(self, **kwargs):
        for key, value in kwargs.items():
            # this should be where the motor is moved; switch to logbook2mouse function for parrot update
            caput(key, value)
        caput(f"{self.mako_prefix}trigger", True, wait=True)
        brightness = caget(f"{self.mako_prefix}brightness")
        return brightness * 100

    def optimize(self):
        self.bounds_transformer = SequentialDomainReductionTransformer()
        self.pbounds = {self.motor_address: (self.motor_min, self.motor_max)}
        self.optimizer = BayesianOptimization(
            f=self.black_box_function,
            pbounds=self.pbounds,
            random_state=1,
            bounds_transformer=self.bounds_transformer,
            acquisition_function=acquisition_function,
        )
        acquisition_function = ExpectedImprovement(xi=1e-4)

        self.optimizer.maximize(
            init_points=10, n_iter=10,
        )

    def photo(self):
        caput(f"{self.mako_prefix}capture", True, wait=True, timeout=5)
        brightness = caget(f"{self.mako_prefix}brightness")
        return brightness


def parse(args=None):
    """Define command-line arguments."""
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(
        description="Take a picture of the current thin film sample by changing its orientation.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "-c",
        "--camera_ioc_prefix",
        default="mako:",
        type=str,
        help="Prefix of the (Mako) camera IOC.",
    )

    parser.add_argument(
        "-m",
        "--motor_pv",
        type=str,
        default="mc0:pitchgi",
        help="Address of the EPICS PV for the relevant motor.",
    )

    parser.add_argument(
        "-l",
        "--motor_lower_limit",
        type=float,
        default=-30,
        help="Minimum value of the motor pv to probe.",
    )

    parser.add_argument(
        "-h",
        "--motor_higher_limit",
        type=float,
        default=0,
        help="Maximum value of the motor pv to probe.",
    )
    args = parser.parse_args(args)
    return args


if __name__ == "__main__":
    args = parse()
    photographer = SurfacePhotographer(
        mako_prefix=args.camera_ioc_prefix,
        motor_address=args.motor_pv,
        motor_max=args.motor_higher_limit,
        motor_min=args.motor_lower_limit,
    )
    photographer.optimize()
    photographer.photo()
