#! -*- coding: utf-8 -*-

# Description    Flame Apply class
##
# Authors:       Manuel Pastor (manuel.pastor@upf.edu), Jose Carlos Gómez (josecarlos.gomez@upf.edu)
##
# Copyright 2018 Manuel Pastor
##
# This file is part of Flame
##
# Flame is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation version 3.
##
# Flame is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
##
# You should have received a copy of the GNU General Public License
# along with Flame.  If not, see <http://www.gnu.org/licenses/>.

import yaml
from flame.stats.space import Space
from flame.util import utils, get_logger

LOG = get_logger(__name__)

class Sapply:

    def __init__(self, parameters, conveyor):

        self.param = parameters
        self.conveyor = conveyor
        self.conveyor.setOrigin('sapply')
        self.X = self.conveyor.getVal('xmatrix')


    def run (self, runtime_param): 
        ''' 

        Runs prediction tasks using internally defined methods

        Most of these methods can be found at the stats folder

        '''

        try:
            with open(runtime_param, 'r') as pfile:
                rtparam = yaml.safe_load(pfile)
        except:
            LOG.error('runtime similarity parameter file not found')
            self.conveyor.setError('runtime similarity parameter file not found')
            return

        try:
            cutoff = rtparam['similarity_cutoff_distance']
            numsel = rtparam['similarity_cutoff_num']
            metric = rtparam['similarity_metric']
        except:
            LOG.error('wrong format in the runtime similarity parameters')
            self.conveyor.setError('wrong format in the runtime similarity parameters')
            return 

        # instances space object
        space = Space(self.param)

        # builds space from idata results
        LOG.info('Starting space searching')
        success, search_results = space.search (self.X, cutoff, numsel, metric)
        if not success:
            self.conveyor.setError(search_results)
            return

        self.conveyor.addVal(
                    search_results,
                    'search_results',
                    'Search results',
                    'result',
                    'objs',
                    'Collection of similar compounds','main')

        LOG.info('Space search finished successfully')

        return
