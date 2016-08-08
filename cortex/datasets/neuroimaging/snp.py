'''SNP dataset class.

'''

from collections import OrderedDict
import numpy as np
from scipy.io import loadmat
from .. import BasicDataset, Dataset
from ...utils.tools import get_paths, warn_kwargs


class SNP(BasicDataset):
    '''SNP dataset class.

    Currently only handled continuous preprocessed data.
    Discrete data TODO

    '''
    def __init__(self, source=None, name='snp', mode='train', convert_one_hot=True, idx=None, **kwargs):
        '''Initialize the SNP dataset.

        Args:
            source: (str): Path to source file.
            name: (str): ID of dataset.
            idx: (Optional[list]): List of indices for train/test/validation
                split.

        '''
        if source is None:
            raise ValueError('No source provided')

        # Fetch SNP data from "source"
        X, Y = self.get_data(source)
        data = {name: X, 'label': Y}

        # balance data for traning, valid, and test parts
        balance = False
        if idx is not None:
            #balance=True
            data[name] = data[name][idx]
            data['label'] = data['label'][idx]

        distributions = {name: 'gaussian', 'label': 'multinomial'}
        super(SNP, self).__init__(data, name=name, balance=balance, distributions=distributions,  mode=mode, **kwargs)

        self.mean_image = self.data[name].mean(axis=0)

    def get_data(self, source):
        '''Fetch the data from source.

        Genetic data is in the matrix format with size Subjec*SNP
        SNP can be either preprocessed or notprocessed
        Labels is a vector with diagnosis info
        Patients are coded with 1 and health control coded with 2

        Args:
            source (dict): file names of genetic data and labels
                {'snp' key for genetic data
                'labels' key for diagnosis }

        '''
        data_path = get_paths()['$data']
        print('Loading genetic data from %s' % data_path)
        if source['snp'].endswith('.mat'):
            X = loadmat(data_path + '/' + source['snp'])
            Y = loadmat(data_path + '/' + source['label'])
            X_key = list(set(X.keys()) - set(['__header__', '__globals__', '__version__']))
            Y_key = list(set(Y.keys()) - set(['__header__', '__globals__', '__version__']))
            if len(X_key)!=1:
                raise ValueError('Found unsufficient number of  header for SNP data')
            if len(Y_key)!=1:
                raise ValueError('Found unsufficient number of header for SNP data labels')
            X = np.float32(X[X_key[0]])
            Y = np.float32(Y[Y_key[0]])
        elif source['snp'].endswith('.txt'):
            X = np.loadtxt(data_path + '/' + source['snp'])
            Y = np.loadtxt(data_path + '/' + source['label'])

        try :
            Chr = loadmat(data_path + '/' + source['chrom_index'])
            Chr_key = list(set(Chr.keys()) - set(['__header__', '__globals__', '__version__']))
            Chr = np.float32(Chr[Chr_key[0]])
            if len(Chr_key)!=1:
                raise ValueError('Found unsufficient number of header for SNP Chromosome Index')

            try :
                chromosomes = source['chromosomes']
                if (chromosomes!=None):
                    if type(chromosomes)==int:
                        chromosomes=[chromosomes]
                    if (len(chromosomes)!=0)&(type(chromosomes)==list):
                        ind_ch = np.where(Chr==chromosomes)
                        X = X[: , ind_ch[0]]
                        print('Using chromosomes: %s' % chromosomes)
                    else:
                        print('Chromosome index is not valid, Using all chromosomes as Default')
                else:
                    print('Chromosomes Index is either empty or None, Using all chromosomes as Default')
            except:
                print(' "Chromosomes" variable cannot found!!!Using all chromosomes as Default')
                pass
        except:
            print('No Chromosome Index data found!! Using all chromosomes')
            pass
        Y.resize(max(Y.shape,))
        return X, Y
