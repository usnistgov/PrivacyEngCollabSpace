import numpy as np
import pandas as pd
import json
from scipy.stats import norm
import pickle
from mbi import Dataset, Domain

class Mechanism:
    """ This class is a template for a mechanism with all the boilerplate code
        already implemented.  subclasses should implement three functions:
            setup, measure, and postprocess

        measure is the only function that is allowed to look at the data, and it must
        be privacy-vetted.  All other code should not need to be checked with very much scrutiny
    """
    def __init__(self, dataset, specs):
        self.dataset = dataset
        self.specs = json.load(open(specs, 'r'))
        domain_info = json.load(open('domain.json'))

        # check consistency for codebook information
        for col in list(domain_info):
            if domain_info[col][-1] < self.specs[col]['maxval']:
                print('Codebook inconsistent for', col)
                del domain_info[col]

        ## look at ground truth data to obtain possible values for state-dependent columns
        df = pd.read_csv(dataset)
        for col in ['SEA', 'METAREA', 'COUNTY', 'CITY', 'METAREAD']:
            domain_info[col] = sorted(df[col].unique())
        ## done using ground truth data 

        domain = { }
        for col in self.specs:
            if col in domain_info:
                domain[col] = len(domain_info[col])
            else:
                domain[col] = self.specs[col]['maxval'] + 1

        domain['INCWAGE_A'] = 52
        domain['INCWAGE_B'] = 8
        del domain['INCWAGE']
        #domain['INCWAGE'] = 5002
        domain['VALUEH'] = 5003
        
        self.domain_info = domain_info 
        self.domain = Domain.fromdict(domain)

    def setup(self):
        """ do any setup needed to run the algorithm here """
        pass

    def load_data(self, path=None):
        """ load the data and discretize the integer/float attributes """
        if path is None:
            path = self.dataset
        df = pd.read_csv(path)
        self.column_order = df.columns

        for col in self.domain_info:
            vals = self.domain_info[col]
            mapping = dict(zip(vals, range(len(vals))))
            df[col] = df[col].map(mapping)

        mapping = { k : k // 100 for k in range(5000) }
        mapping[999998] = 51
        mapping.update({ i : 50 for i in range(5000, 999998) })
        df['INCWAGE_A'] = df['INCWAGE'].map(mapping)

        mod_mapping = { k : 0 for k in range(5000, 999999) }
        for i in range(5001):
            if i % 100 == 0:
                mod_mapping[i] = 0
            elif i % 20 == 0:
                mod_mapping[i] = 1
            elif i % 50 == 0:
                mod_mapping[i] = 2
            elif i % 25 == 0:
                mod_mapping[i] = 3
            elif i % 10 == 0:
                mod_mapping[i] = 4
            elif i % 5 == 0:
                mod_mapping[i] = 5
            elif i % 2 == 0:
                mod_mapping[i] = 6
            else:
                mod_mapping[i] = 7

        df['INCWAGE_B'] = df['INCWAGE'].map(mod_mapping)

        mapping = {}
        for i in range(9999998):
            if i <= 25000:
                mapping[i] = i // 5
            else:
                mapping[i] = 5000

        mapping[9999998] = 5001
        mapping[9999999] = 5002
        df['VALUEH'] = df['VALUEH'].map(mapping) 
    

        return Dataset(df, self.domain)


    def measure(self):
        """ load the data and measure things about it
        save the measuremnts taken, but do not save the data 
        this is the only function that needs to be vetted for privacy
        """
        pass

    def postprocess(self):
        """ post-process the measurments taken into a synthetic dataset over discrete attributes
        """

    def transform_domain(self):
        """ convert the synthetic discrete data back to the original domain
            and add any missing columns with a default value """
        df = self.synthetic.df

        mod_mapping = { k : [] for k in range(8) }
        for i in range(100):
            if i % 100 == 0:
                mod_mapping[0].append(i)
            elif i % 20 == 0:
                mod_mapping[1].append(i)
            elif i % 50 == 0:
                mod_mapping[2].append(i)
            elif i % 25 == 0:
                mod_mapping[3].append(i)
            elif i % 10 == 0:
                mod_mapping[4].append(i)
            elif i % 5 == 0:
                mod_mapping[5].append(i)
            elif i % 2 == 0:
                mod_mapping[6].append(i)
            else:
                mod_mapping[7].append(i)

        def foo(g):
            vals = mod_mapping[g.name]
            g['INCWAGE_C'] = np.random.choice(vals, g.shape[0])
            return g
        df = df.groupby('INCWAGE_B').apply(foo)
        
        df['INCWAGE'] = df['INCWAGE_A']*100 + df['INCWAGE_C']
        df.loc[df.INCWAGE_A == 50, 'INCWAGE'] = 5000
        df.loc[df.INCWAGE_A == 51, 'INCWAGE'] = 999998

        for col in self.specs:
            if not col in df:
                df[col] = 0
        
        for col in self.domain_info:
            vals = self.domain_info[col]
            mapping = dict(zip(range(len(vals)), vals))
            df[col] = df[col].map(mapping)
 
        mapping = dict(zip(range(5001), range(0,25001,5)))
        mapping[5001] = 9999998
        mapping[5002] = 9999999
        df['VALUEH'] = df['VALUEH'].map(mapping) 
   
        self.synthetic = df[self.column_order]
        return df

    def run(self, epsilon, delta = 2.2820610e-12, save=None):
        """ Run the mechanism at the given privacy level and return teh synthetic data

        :param epsilon: the privacy budget
        :param delta: privacy parameter
        :param save: location to save the synthetic data
        :return: the synthetic data in the same format as original data
        """
        self.epsilon = epsilon
        self.delta = delta
        self.save = save
        self.setup()
        self.measure()
        self.postprocess()
        self.transform_domain()
        if save is not None:
            self.synthetic.to_csv(save, index=False)
        return self.synthetic

if __name__ == '__main__':
    from IPython import embed
    mech = Mechanism()
    df = mech.load_data().df
    mech.synthetic = df
    mech.transform_domain()
    df2 = mech.synthetic
    #embed()
