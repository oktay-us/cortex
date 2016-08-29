'''
SNP dataset class.
'''

from scipy.io import loadmat
import logging
import numpy as np
import pprint
from progressbar import (
    Bar,
    Percentage,
    ProgressBar,
    Timer
)
import yaml
from .ni_dataset import NeuroimagingDataset
from ...utils.tools import resolve_path
np.seterr(all='raise')

class SNP(NeuroimagingDataset):
    _init_steps = 8
    '''SNP dataset class.

    Currently only handled continuous preprocessed data.
    Discrete data TODO

    '''
    def __init__(self, source=None, name='snp', mode='train', balance=False, distribution='gaussian', one_hot=True, idx=None, **kwargs):

        '''Initialize the SNP dataset.

        Args:
            source: (str): Path to source file.
            name: (str): ID of dataset.
            idx: (Optional[list]): List of indices for train/test/validation
                split.

        '''
        if source is None:
            raise TypeError('`source` argument must be provided')

        source = resolve_path(source)

        self.logger = logging.getLogger('.'.join([self.__module__,
                                                  self.__class__.__name__]))
        self.logger.info('Loading %s from %s' % (name, source))

        widgets = ['Forming %s dataset: ' % name , '(', Timer(), ') [',
                   Percentage(), ']']
        self.pbar = ProgressBar(widgets=widgets, maxval=self._init_steps).start()
        self.progress = 0

        # Fetch SNP data from "source"
        X, Y = self.get_data(source)

        data = {'input': X, 'labels': Y}

        # balance data for traning, valid, and test parts
        #balance = False
        #if idx is not None:
        #    balance=True
        #    data[name] = data[name][idx]
        #    data['label'] = data['label'][idx]
        import ipdb
        ipdb.set_trace()
        distributions = {'input': distribution, 'label': 'multinomial'}
        super(SNP, self).__init__(data, name=name, balance=balance, distributions=distributions,  mode=mode, one_hot=one_hot, **kwargs)

        #self.mean_image = self.data['input'].mean(axis=0)

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
        self.logger.info('Loading file locations from %s' % source)
        source_dict = yaml.load(open(source))
        self.update_progress()
        self.logger.debug('Source locations: \n%s' % pprint.pformat(source_dict))
        data_path = resolve_path(source_dict['snp'])

        label_path = resolve_path(source_dict['labels'])

        print('Loading genetic data from %s' % data_path)
        if data_path.endswith('.mat'):
            X = loadmat(data_path)
            Y = loadmat(label_path)
            X_key = list(set(X.keys()) - set(['__header__', '__globals__', '__version__']))
            Y_key = list(set(Y.keys()) - set(['__header__', '__globals__', '__version__']))
            if len(X_key)!=1:
                raise ValueError('Found unsufficient number of  header for SNP data')
            if len(Y_key)!=1:
                raise ValueError('Found unsufficient number of header for SNP data labels')
            X = np.float32(X[X_key[0]])
            Y = np.float32(Y[Y_key[0]])
        elif data_path.endswith('.txt'):
            X = np.loadtxt(data_path)
            Y = np.loadtxt(data_path)

        try :
            chrom_index = source_dict['chrom_index']
            Chr = loadmat(chrom_index)
            Chr_key = list(set(Chr.keys()) - set(['__header__', '__globals__', '__version__']))
            Chr = np.float32(Chr[Chr_key[0]])
            if len(Chr_key)!=1:
                raise ValueError('Found unsufficient number of header for SNP Chromosome Index')

            try :
                chromosomes = source_dict['chromosomes']
                if (chromosomes!=None):
                    if type(chromosomes)==int:
                        chromosomes=[chromosomes]
                    if (len(chromosomes)!=0)&(type(chromosomes)==list):
                        ind_ch = np.where(Chr==chromosomes)
                        X = X[: , ind_ch[0]]
                        self.logger.info('Using chromosomes: %s' % chromosomes)
                    else:
                        self.logger.info('Chromosome index is not valid, Using all chromosomes as Default')
                else:
                    self.logger.info('Chromosomes Index is either empty or None, Using all chromosomes as Default')
            except:
                self.logger.info(' "Chromosomes" variable cannot found!!!Using all chromosomes as Default')
                pass
        except:
            self.logger.info('No Chromosome Index data found!! Using all chromosomes')
            pass
        Y.resize(max(Y.shape,))
        self.n_subjects = X.shape[0]
        return X, Y

_classes = {'SNP' : SNP}