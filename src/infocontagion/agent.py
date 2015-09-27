#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
from abmtemplate.baseagent import BaseAgent

class Agent(BaseAgent):
    identifier = ""
    parameters = {}
    state_variables = {}

    def get_identifier(self):
        return self.identifier
    def set_identifier(self, _value):
        super(Agent, self).set_identifier(_value)

    def get_parameters(self):
        return self.parameters
    def set_parameters(self, _value):
        super(Agent, self).set_parameters(_value)

    def get_state_variables(self):
        return self.state_variables
    def set_state_variables(self, _value):
        super(Agent, self).set_state_variables(_value)


    def __init__(self, _identifier, _params, _variables):
        super(Agent, self).__init__(_identifier, _params, _variables)
        # initialize variables used in any of the methods

    def __str__(self):
        ret_str = super(Agent, self).__str__()
        return ret_str


    def calculate_theta_A(self):
        try:
            value = (self.u1_A-self.u2_AB)/(self.u2_AG-self.u2_AB)
        except:
            value = 0.0
        if (value < 0.0):
            value = 0.0
        if (value > 0.5):
            value = 0.5
        return value

    def calculate_theta_CE(self):
        try:
            value = (self.u_d_ce - self.u2_Bce)/(self.u2_Gce - self.u2_Bce)
        except:
            value = 0.0
        if (value < 0.0):
            value = 0.0
        if (value > 1.0):
            value = 1.0
        return value


    def calculate_theta_H(self):
        try:
            value = (self.u_d_H-self.u_HB)/(self.u_HG-self.u_HB)
        except:
            value = 0.0
        if (value < 0.0):
            value = 0.0
        if (value > 0.5):
            value = 0.5
        return value

    def calculate_theta_L(self):
        a_H = self.get_parameters()['q']*self.calculate_theta_H()
        try:
            value = ( a_H*(self.u_d_LD-self.u_LBD) + (1.0-a_H)*(self.u_d_LN-self.u_LBN) ) / \
                    ( a_H*(self.u_LGD-self.u_LBD) + (1.0-a_H)*(self.u_LGN-self.u_LBN) )
        except:
            value = 0.0
        if (value < 0.0):
            value = 0.0
        if (value > 0.5):
            value = 0.5
        return value

    def calculate_theta_LN(self):
        try:
            value = (self.u_d_LN - self.u_LBN) / (self.u_LGN - self.u_LBN)
        except:
            value = 0.0
        if (value < 0.0):
            value = 0.0
        if (value > 0.5):
            value = 0.5
        return value

    def calculate_theta_LD(self):
        q_H = self.get_parameters()['q']
        try:
            value = ( q_H*(self.u_d_LD - self.u_LBD) + (1.0 - q_H)*(self.u_d_LN - self.u_LBN) ) / \
                    ( q_H*(self.u_LGD - self.u_LBD) + (1.0 - q_H)*(self.u_LGN - self.u_LBN) )
        except:
            value = 0.0
        if (value < 0.0):
            value = 0.0
        if (value > 0.5):
            value = 0.5
        return value

    def calculate_theta(self):
        try:
            value = (self.u_dc - self.u_Bc)/(self.u_Gc - self.u_Bc)
        except:
            value = 0.0
        if (value < 0.0):
            value = 0.0
        if (value > 0.5):
            value = 0.5
        return value


    def compute_ancillary_variables(self, R, beta, lamb, phi, eta):
        # to ease writing, introduce local variables for state variables
        d1 = self.get_state_variables()['d1']
        y = self.get_state_variables()['y']
        b = self.get_state_variables()['b']

        #
        # calculate variables for autarky and comp. eq.
        #
        self.c1_A = y + (1-y)*beta
        self.c2_AB = y
        self.c2_AG = y + (1-y)*R
        self.u1_A = self.compute_utility(self.c1_A)
        self.u2_AB = self.compute_utility(self.c2_AB)
        self.u2_AG = self.compute_utility(self.c2_AG)

        self.theta_A = self.calculate_theta_A()

        self.d_ce = y + (1.0-y)*beta
        self.c2_Gce = (y-lamb*d1 + (1.0-y)*R)/(1.0-lamb)
        self.c2_Bce = (y-lamb*d1)/(1.0-lamb)
        self.u_d_ce = self.compute_utility(self.d_ce)
        self.u2_Gce = self.compute_utility(self.c2_Gce)
        self.u2_Bce = self.compute_utility(self.c2_Bce)

        self.theta_CE = self.calculate_theta_CE()

        #
        # recalculate all values with the current values for (d1, y, b)
        #
        lambda_H = lamb + eta
        lambda_L = lamb - eta

        self.d_H = y + beta*(1.0-y) + b
        self.c_HB = (y-lambda_H*d1-(phi-1.0)*b)/(1.0-lambda_H)
        self.c_HG = (R*(1.0-y)+y-lambda_H*d1-(phi-1.0)*b)/(1.0-lambda_H)

        self.u_HB = self.compute_utility(self.c_HB)
        self.u_HG = self.compute_utility(self.c_HG)
        self.u_d_H = self.compute_utility(self.d_H)
        self.u_d_1 = self.compute_utility(d1)

        #
        # REGION L
        #
        self.d_LN = y+beta*(1.0-y)+b*(beta*phi-1.0)
        self.d_LD = y+beta*(1.0-y)-b
        self.c_LGN = (R*(1.0-y)+y-lambda_L*d1+(phi-1.0)*b)/(1.0-lambda_L)
        self.c_LGD = (R*(1.0-y)+y-lambda_L*d1-b)/(1.0-lambda_L)
        self.c_LBN = (y-lambda_L*d1+(phi-1.0)*b)/(1.0-lambda_L)
        self.c_LBD = (y-lambda_L*d1-b)/(1.0-lambda_L)

        self.u_LGN = self.compute_utility(self.c_LGN)
        self.u_LGD = self.compute_utility(self.c_LGD)
        self.u_LBN = self.compute_utility(self.c_LBN)
        self.u_LBD = self.compute_utility(self.c_LBD)
        self.u_d_LN = self.compute_utility(self.d_LN)
        self.u_d_LD = self.compute_utility(self.d_LD)

        self.theta_H = self.calculate_theta_H()
        self.theta_L = self.calculate_theta_L()
        self.theta_LN = self.calculate_theta_LN()
        self.theta_LD = self.calculate_theta_LD()

        # Pure common shock
        self.dc = y + (1-y)*beta
        self.c_Gc = ((1.0-y)*R + y - lamb*d1)/(1.0-lamb)
        self.c_Bc = (y-lamb*d1)/(1.0-lamb)

        self.u_dc = self.compute_utility(self.dc)
        self.u_Gc = self.compute_utility(self.c_Gc)
        self.u_Bc = self.compute_utility(self.c_Bc)

        self.theta = self.calculate_theta()


    def compute_utility(self, _consumption):
        _value = None
        global nan
        nan = 100000000000000.0

        rho = self.get_parameters()['rho']

        if (_consumption < 0.0):
            #print "ERROR: consumption negative: " + str(consumption)
            return -nan
        else:
            if (rho == 0.0): # just for debugging
                _value = _consumption
            if (rho == 1.0): # just for debugging
                try:
                    _value = math.log(_consumption)
                except:
                    _value = -nan
            else:
                # CRRA with rho > 1.0 produces negative utility for consumption < 1.0
                try:
                    _value = (pow(_consumption,(1.0-rho)))/(1.0-rho)
                except:
                    _value = -nan

        return _value

