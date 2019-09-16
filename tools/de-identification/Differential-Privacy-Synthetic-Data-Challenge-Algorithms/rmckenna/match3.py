from mechanism import Mechanism
import mbi
from mbi import Domain, Factor, FactoredInference, GraphicalModel, Dataset
import matrix
import argparse
import numpy as np
from scipy import sparse, optimize
from privacy.analysis.rdp_accountant import compute_rdp, get_privacy_spent
from functools import reduce
import os

def transform_data(data, supports):
    df = data.df.copy()
    newdom = {}
    for col in data.domain:
        support = supports[col]
        size = support.sum()
        newdom[col] = int(size)
        if size < support.size:
            newdom[col] += 1
        mapping = {}
        idx = 0
        for i in range(support.size):
            mapping[i] = size
            if support[i]:
                mapping[i] = idx
                idx += 1
        assert idx == size
        df[col] = df[col].map(mapping)
    newdom = Domain.fromdict(newdom)
    return Dataset(df, newdom)

def reverse_data(data, supports):
    df = data.df.copy()
    newdom = {}
    for col in data.domain:
        support = supports[col]
        mx = support.sum()
        newdom[col] = int(support.size)
        idx, extra = np.where(support)[0], np.where(~support)[0]
        mask = df[col] == mx
        if extra.size == 0:
            pass
        else:
            df.loc[mask, col] = np.random.choice(extra, mask.sum())
        df.loc[~mask, col] = idx[df.loc[~mask, col]]
    newdom = Domain.fromdict(newdom)
    return Dataset(df, newdom)

def moments_calibration(round1, round2, eps, delta):
    # round1: L2 sensitivity of round1 queries
    # round2: L2 sensitivity of round2 queries
    # works as long as eps >= 0.01; if larger, increase orders
    orders = range(2, 4096)

    def obj(sigma):
        rdp1 = compute_rdp(1.0, sigma/round1, 1, orders)
        rdp2 = compute_rdp(1.0, sigma/round2, 1, orders)
        rdp = rdp1 + rdp2
        privacy = get_privacy_spent(orders, rdp, target_delta=delta)
        return privacy[0] - eps + 1e-8
    low = 1.0
    high = 1.0
    while obj(low) < 0:
        low /= 2.0
    while obj(high) > 0:
        high *= 2.0
    sigma = optimize.bisect(obj, low, high)
    assert obj(sigma) - 1e-8 <= 0, 'not differentially private' # true eps <= requested eps
    return sigma

class Match3(Mechanism):

    def __init__(self, dataset, specs, iters=1000, weight3=1.0, warmup=False):
        Mechanism.__init__(self, dataset, specs)
        self.iters = iters
        self.weight3 = weight3
        self.warmup = warmup
        self.elimination_order = None

        Qa = np.zeros((5,52))
        Qa[0,0] = 1
        Qa[1,1:10] = 1
        Qa[2,10:20] = 1
        Qa[3,20:51] = 1
        Qa[4,51] = 1

        self.Q_INCWAGE = Qa
    
    def setup(self):
        self.round1 = list(self.domain.attrs)
        self.round2 = [('COUNTY', 'SUPDIST'), ('COUNTY', 'SEA'), ('COUNTY', 'MIGSEA5'), ('COUNTY', 'METAREA'), ('COUNTY', 'METAREAD'), ('COUNTY', 'METRO'), ('URBAN', 'URBPOP'), ('CITY', 'INCWAGE_A'), ('CITY', 'CITYPOP'), ('CITYPOP', 'URBPOP'), ('CITYPOP', 'SIZEPL'), ('CITYPOP', 'SUPDIST'), ('CITYPOP', 'ENUMDIST'), ('CITYPOP', 'WARD'), ('CITYPOP', 'FARM'), ('GQ', 'GQFUNDS'), ('GQ', 'OWNERSHPD'), ('GQ', 'SPLIT'), ('GQTYPE', 'GQTYPED'), ('GQTYPED', 'ENUMDIST'), ('OWNERSHP', 'OWNERSHPD'), ('OWNERSHP', 'RENT'), ('OWNERSHP', 'VALUEH'), ('RENT', 'ENUMDIST'), ('ENUMDIST', 'RACED'), ('SLREC', 'UIND'), ('RESPONDT', 'AGE'), ('FAMSIZE', 'MARST'), ('NCHLT5', 'AGE'), ('SEX', 'INCWAGE_A'), ('AGE', 'EMPSTATD'), ('AGE', 'HIGRADED'), ('AGE', 'MARST'), ('AGE', 'MBPLD'), ('AGE', 'SCHOOL'), ('AGE', 'AGEMONTH'), ('MARRNO', 'CHBORN'), ('MARRNO', 'UIND'), ('AGEMARR', 'CHBORN'), ('RACE', 'RACED'), ('HISPAN', 'HISPAND'), ('HISPAND', 'HISPRULE'), ('BPL', 'BPLD'), ('BPLD', 'MBPLD'), ('BPLD', 'CITIZEN'), ('MBPL', 'MBPLD'), ('MBPLD', 'FBPLD'), ('FBPL', 'FBPLD'), ('FBPLD', 'HISPRULE'), ('FBPLD', 'NATIVITY'), ('NATIVITY', 'UOCC'), ('NATIVITY', 'MTONGUED'), ('MTONGUE', 'MTONGUED'), ('SPANNAME', 'HISPRULE'), ('HIGRADE', 'HIGRADED'), ('HIGRADE', 'EDUC'), ('HIGRADED', 'EDUCD'), ('EMPSTAT', 'EMPSTATD'), ('EMPSTATD', 'LABFORCE'), ('EMPSTATD', 'OCC'), ('EMPSTATD', 'HRSWORK1'), ('EMPSTATD', 'DURUNEMP'), ('OCC', 'OCC1950'), ('OCC', 'NPBOSS50'), ('OCC', 'ERSCOR50'), ('OCC', 'PRESGL'), ('OCC', 'EDSCOR50'), ('OCC', 'SEI'), ('OCC', 'IND'), ('OCC', 'CLASSWKRD'), ('OCC', 'INCWAGE_A'), ('OCC1950', 'OCCSCORE'), ('IND', 'IND1950'), ('CLASSWKR', 'CLASSWKRD'), ('WKSWORK1', 'WKSWORK2'), ('WKSWORK1', 'INCWAGE_A'), ('HRSWORK1', 'HRSWORK2'), ('UOCC', 'UIND'), ('UOCC', 'UOCC95'), ('UOCC', 'VET1940'), ('UOCC', 'SSENROLL'), ('UIND', 'UCLASSWK'), ('UIND', 'VETPER'), ('INCWAGE_A', 'INCNONWG'), ('MIGRATE5', 'MIGPLAC5'), ('MIGRATE5D', 'MIGPLAC5'), ('MIGRATE5D', 'SAMEPLAC'), ('MIGRATE5D', 'SAMESEA5'), ('MIGPLAC5', 'MIGSEA5'), ('MIGMET5', 'MIGSEA5'), ('MIGMET5', 'MIGTYPE5'), ('MIGCITY5', 'MIGSEA5'), ('MIGSEA5', 'MIGCOUNTY'), ('VETSTAT', 'VETSTATD'), ('VETSTAT', 'VETPER'), ('VETSTAT', 'VETWWI'), ('VET1940', 'VETCHILD')]

        self.round2 += [('SEX', 'CITY'), ('SEX', 'CITY', 'INCWAGE_A'), ('INCWAGE_A', 'INCWAGE_B')]
        self.round2 += [('SUPDIST', 'ENUMDIST'), ('SUPDIST', 'FARM'), ('ENUMDIST', 'WARD'), ('EMPSTATD', 'MARST'), ('EMPSTATD', 'HIGRADED'), ('EMPSTATD', 'RESPONDT'), ('MARST', 'NCHLT5'), ('MARST', 'MBPLD'), ('AGE', 'EMPSTATD', 'MARST'), ('AGE', 'EMPSTATD', 'HIGRADED'), ('AGE', 'EMPSTATD', 'RESPONDT'), ('AGE', 'MARST', 'NCHLT5'), ('AGE', 'MARST', 'MBPLD'), ('AGE', 'FAMSIZE'), ('MARST', 'AGE', 'FAMSIZE'), ('FBPLD', 'AGE'), ('AGE', 'BPLD'), ('MBPLD', 'FBPLD', 'AGE'), ('MBPLD', 'AGE', 'BPLD'), ('LABFORCE', 'AGE'), ('AGE', 'OCC'), ('OCC', 'HRSWORK1'), ('EMPSTATD', 'LABFORCE', 'AGE'), ('EMPSTATD', 'AGE', 'OCC'), ('EMPSTATD', 'OCC', 'HRSWORK1'), ('IND', 'INCWAGE_A'), ('CLASSWKRD', 'INCWAGE_A'), ('EMPSTATD', 'INCWAGE_A'), ('OCC', 'IND', 'INCWAGE_A'), ('OCC', 'CLASSWKRD', 'INCWAGE_A'), ('OCC', 'EMPSTATD', 'INCWAGE_A'), ('SEX', 'OCC'), ('CITY', 'OCC'), ('OCC', 'WKSWORK1'), ('OCC', 'INCNONWG'), ('INCWAGE_A', 'SEX', 'OCC'), ('INCWAGE_A', 'CITY', 'OCC'), ('INCWAGE_A', 'OCC', 'WKSWORK1'), ('INCWAGE_A', 'OCC', 'INCNONWG'), ('MIGMET5', 'COUNTY'), ('COUNTY', 'MIGCITY5'), ('COUNTY', 'MIGCOUNTY'), ('MIGPLAC5', 'MIGCOUNTY'), ('MIGSEA5', 'MIGMET5', 'COUNTY'), ('MIGSEA5', 'COUNTY', 'MIGCITY5'), ('MIGSEA5', 'COUNTY', 'MIGCOUNTY'), ('MIGSEA5', 'MIGPLAC5', 'MIGCOUNTY')]
                                        
    def measure(self):
        data = self.load_data()
        # round1 and round2 measurements will be weighted to have L2 sensitivity 1
        sigma = moments_calibration(1.0, 1.0, self.epsilon, self.delta)
        print('NOISE LEVEL:', sigma)

        weights = np.ones(len(self.round1))
        weights[self.round1.index('INCWAGE_A')] *= 2.0
        weights /= np.linalg.norm(weights) # now has L2 norm = 1

        supports = {}
  
        self.measurements = []
        for col, wgt in zip(self.round1, weights):
            ##########################
            ### Noise-addition step ##
            ##########################
            proj = (col,)
            hist = data.project(proj).datavector()
            noise = sigma*np.random.randn(hist.size)
            y = wgt*hist + noise
          
            #####################
            ## Post-processing ##
            #####################

            if col in ['INCWAGE_A', 'SEA', 'METAREA', 'COUNTY', 'CITY', 'METAREAD']:
                sup = np.ones(y.size, dtype=bool)
            else:
                sup = y >= 3*sigma

            supports[col] = sup
            print(col, self.domain.size(col), sup.sum())

            if sup.sum() == y.size:
                y2 = y
                I2 = matrix.Identity(y.size)
            else:
                y2 = np.append(y[sup], y[~sup].sum())
                I2 = np.ones(y2.size)
                I2[-1] = 1.0 / np.sqrt(y.size - y2.size + 1.0)
                y2[-1] /= np.sqrt(y.size - y2.size + 1.0)
                I2 = sparse.diags(I2)

            self.measurements.append( (I2, y2/wgt, 1.0/wgt, proj) )

        self.supports = supports 
        # perform round 2 measurments over compressed domain
        data = transform_data(data, supports)
        self.domain = data.domain

        self.round2 = [cl for cl in self.round2 if self.domain.size(cl) < 1e6]
        weights = np.ones(len(self.round2))
        weights[self.round2.index(('SEX','CITY','INCWAGE_A'))] *= self.weight3
        weights[self.round2.index(('SEX','CITY'))] *= 2.0
        weights[self.round2.index(('SEX','INCWAGE_A'))] *= 2.0
        weights[self.round2.index(('CITY','INCWAGE_A'))] *= 2.0
        weights /= np.linalg.norm(weights) # now has L2 norm = 1
   
        for proj, wgt in zip(self.round2, weights):
            #########################
            ## Noise-addition step ##
            #########################
            hist = data.project(proj).datavector()
            if proj == ('SEX', 'CITY', 'INCWAGE_A'):
                dom = self.domain.project(proj).shape
                I = sparse.eye(dom[0] * dom[1])
                Q = sparse.kron(I, self.Q_INCWAGE).tocsr()
            elif proj == ('CITY', 'INCWAGE_A'):
                I = sparse.eye(self.domain.size('CITY'))
                Q = sparse.kron(I, self.Q_INCWAGE).tocsr()
            else: 
                Q = matrix.Identity(hist.size)

            noise = sigma*np.random.randn(Q.shape[0])
            y = wgt*Q.dot(hist) + noise
            self.measurements.append( (Q, y/wgt, 1.0/wgt, proj) )

    def postprocess(self):
        iters = self.iters
        domain = self.domain
        engine = FactoredInference(domain,
                                    structural_zeros=None,
                                    iters=500,
                                    log=True,
                                    warm_start=True,
                                    elim_order=self.elimination_order)
        self.engine = engine
        cb = mbi.callbacks.Logger(engine)

        if self.warmup:
            engine._setup(self.measurements, None)
            oneway = {}
            for i in range(len(self.round1)):
                p = self.round1[i]
                y = self.measurements[i][1]
                y = np.maximum(y, 1)
                y /= y.sum()
                oneway[p] = Factor(self.domain.project(p), y)
            marginals = {}
            for cl in engine.model.cliques:
                marginals[cl] = reduce(lambda x,y: x*y, [oneway[p] for p in cl])

            theta = engine.model.mle(marginals)
            engine.potentials = theta
            engine.marginals = engine.model.belief_prop_fast(theta)

        checkpt = self.save[:-4] + '-checkpt.csv'
        for i in range(self.iters // 500):
            
            engine.infer(self.measurements, engine='MD', callback=cb)

            if i % 4 == 3:
                self.synthetic = engine.model.synthetic_data()
                self.synthetic = reverse_data(self.synthetic, self.supports)
                self.transform_domain()
                self.synthetic.to_csv(checkpt, index=False)
   
        if os.path.exists(checkpt):
            os.remove(checkpt)

        self.synthetic = engine.model.synthetic_data()
        self.synthetic = reverse_data(self.synthetic, self.supports)

def default_params():
    """
    Return default parameters to run this program

    :returns: a dictionary of default parameter settings for each command line argument
    """
    params = {}
    params['dataset'] = 'competitor_pack/data/colorado.csv'
    params['specs'] = 'competitor_pack/data/colorado-specs.json'
    params['epsilon'] = 1.0
    params['delta'] = 2.2820544e-12
    params['save'] = 'out.csv'
    
    return params

if __name__ == '__main__':

    description = ''
    formatter = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser(description=description, formatter_class=formatter)
    parser.add_argument('--dataset', help='path to dataset csv file')
    parser.add_argument('--specs', help='path to specs json file')
    parser.add_argument('--epsilon', type=float, help='privacy parameter')
    parser.add_argument('--delta', type=float, help='privacy parameter')
    parser.add_argument('--save', help='path to save synthetic data to')

    parser.set_defaults(**default_params())
    args = parser.parse_args()

    if args.epsilon <= 0.3:
        iters = 7500
        weight3 = 8.0
    elif args.epsilon >= 4.0:
        iters = 10000
        weight3 = 4.0
    else:
        iters = 7500
        weight3 = 6.0

    mech = Match3(args.dataset, args.specs, iters=iters, weight3=weight3, warmup=True)

    mech.run(args.epsilon, args.delta, args.save)
