"""This script is used to characterize the performance of various featurization
methods on TCRSeq data from 7 Human Antigens."""

from DeepTCR.DeepTCR import DeepTCR_U
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import pdist, squareform
import seaborn as sns
from NN_Assessment_utils import *
import pickle
import os

#Instantiate training object
DTCRU = DeepTCR_U('Human_U')
#Load Data
DTCRU.Get_Data(directory='../../Data/Human_Antigens',Load_Prev_Data=False,aggregate_by_aa=True,
               aa_column_beta=0,count_column=1,v_beta_column=2,j_beta_column=3)

#Get distances from various methods
#VAE_- Genes
DTCRU.Train_VAE(Load_Prev_Data=False,use_only_gene=True)
distances_vae_gene = pdist(DTCRU.features, metric='euclidean')

# #VAE_- Sequencs Alone
DTCRU.Train_VAE(Load_Prev_Data=False,use_only_seq=True)
distances_vae_seq = pdist(DTCRU.features, metric='euclidean')

#VAE_- Gene+Sequencs
DTCRU.Train_VAE(Load_Prev_Data=False)
distances_vae_seq_gene = pdist(DTCRU.features, metric='euclidean')

#Hamming
distances_hamming = pdist(np.squeeze(DTCRU.X_Seq_beta, 1), metric='hamming')

#Kmer
kmer_features = kmer_search(DTCRU.beta_sequences)
distances_kmer = pdist(kmer_features, metric='euclidean')

#Global Seq-Align
# distances_seqalign = pairwise_alignment(DTCRU.beta_sequences)
# with open('Human_seqalign.pkl','wb') as f:
#     pickle.dump(distances_seqalign,f)

with open('Human_seqalign.pkl','rb') as f:
    distances_seqalign = pickle.load(f)

distances_seqalign = distances_seqalign + distances_seqalign.T
distances_seqalign = squareform(distances_seqalign)

distances_list = [distances_vae_seq,distances_vae_gene,distances_vae_seq_gene,distances_hamming,distances_kmer,distances_seqalign]
names = ['VAE-Seq','VAE-Gene','VAE-Seq-Gene','Hamming','K-mer','Global-Seq-Align']


dir_results = 'Human_Results'
if not os.path.exists(dir_results):
    os.makedirs(dir_results)

#Assess performance metrtics via K-Nearest Neighbors
df_metrics = Assess_Performance_KNN(distances_list,names,DTCRU.class_id,dir_results)
Plot_Performance(df_metrics,dir_results)

subdir = 'Performance_Summary'
if not os.path.exists(os.path.join(dir_results,subdir)):
    os.makedirs(os.path.join(dir_results,subdir))

for m in np.unique(df_metrics['Metric']):
    sns.catplot(data=df_metrics[df_metrics['Metric']==m],x='Algorithm',y='Value',kind='violin')
    plt.ylabel(m)
    plt.xticks(rotation=45)
    plt.xlabel('')
    plt.subplots_adjust(bottom=0.25)
    plt.ylabel(m,fontsize=14)
    plt.xticks(fontsize=12)
    plt.savefig(os.path.join(dir_results,subdir,m+'.eps'))

method = 'F1_Score'
from scipy.stats import ttest_rel
df_test = df_metrics[df_metrics['Metric']==method]
idx_1 = df_test['Algorithm'] == 'K-mer'
idx_2 = df_test['Algorithm'] == 'Global-Seq-Align'
t,p_val = ttest_rel(df_test[idx_1]['Value'],df_test[idx_2]['Value'])
print(p_val)

