import numpy as np
from .basic_neuron import Neuron
from .b_splines import get_bsplines
from .act import tanh_act, sigmoid, relu, silu


class KANNeuron(Neuron):

    def __init__(self, n_in, n_weights_per_edge, x_bounds, weights_range=None, get_edge_fun=get_bsplines, **kwargs):
        self.x_bounds = x_bounds
        super().__init__(n_in, num_weights_per_edge=n_weights_per_edge, weights_range=weights_range)
        self.edge_fun, self.edge_fun_der = get_edge_fun(self.x_bounds, self.num_weights_per_edge, **kwargs)

    def compute_edge_values(self):
        # apply edge functions
        self.phi_x_mat = np.array([self.edge_fun[b](self.input_values) for b in self.edge_fun]).T
        self.phi_x_mat[np.isnan(self.phi_x_mat)] = 0
        self.edge_values = (self.weights * self.phi_x_mat).sum(axis=1)

    def compute_output_value(self):
        # note: node function <- tanh to avoid any update of spline grids
        self.output_value = tanh_act(sum(self.edge_values.flatten()), get_derivative=False)

    def compute_derivative_output_wrt_edge(self):
        self.derivative_output_wrt_edge = tanh_act(sum(self.edge_values.flatten()), get_derivative=True) * np.ones(self.num_inputs)

    def compute_derivative_edge_wrt_weights(self):
        self.derivative_edge_wrt_weights = self.phi_x_mat

    def compute_derivative_edge_wrt_input(self):
        phi_x_der_mat = np.array([self.edge_fun_der[b](self.input_values) if self.edge_fun[b](self.input_values) is not None else 0
                                  for b in self.edge_fun_der]).T  # shape (n_in, n_weights_per_edge)
        phi_x_der_mat[np.isnan(phi_x_der_mat)] = 0
        self.derivative_edge_wrt_input = (self.weights * phi_x_der_mat).sum(axis=1)

    def compute_derivative_output_wrt_bias(self):
        # no bias in KAN!
        self.derivative_output_wrt_bias = 0

