from DeepTCR.DeepTCR_U import DeepTCR_U
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from multiprocessing import Pool
from scipy.spatial.distance import pdist, squareform
from scipy.stats import spearmanr, chi2_contingency
import seaborn as sns
from NN_Assessment_utils import *
import pickle
import os
from scipy.cluster.hierarchy import linkage,fcluster


#Instantiate training object
DTCRU = DeepTCR_U('Clustering_Metrics')

p = Pool(40)

#VAE_- Genes
DTCRU.Get_Data(directory='../Data/Sidhom',Load_Prev_Data=False,aggregate_by_aa=True,aa_column_beta=1,count_column=None,
               v_beta_column=7,d_beta_column=14,j_beta_column=21,p=p)
# DTCRU.Get_Data(directory='../Data/Dash/Traditional/Mouse',Load_Prev_Data=False,aggregate_by_aa=True,
#                aa_column_alpha=None,aa_column_beta=1,count_column=2,v_alpha_column=None,j_alpha_column=None,v_beta_column=5,j_beta_column=6)

DTCRU.Train_VAE(accuracy_min=0.9, Load_Prev_Data=False,use_only_gene=True)
distances_vae_gene = pdist(DTCRU.features, metric='euclidean')

DTCRU = DeepTCR_U('Clustering_Metrics')
# #VAE_- Sequencs Alone
DTCRU.Get_Data(directory='../Data/Sidhom',Load_Prev_Data=False,aggregate_by_aa=True,aa_column_beta=1,count_column=None,
               v_beta_column=None,d_beta_column=None,j_beta_column=None,p=p)
# DTCRU.Get_Data(directory='../Data/Dash/Traditional/Mouse',Load_Prev_Data=False,aggregate_by_aa=True,
#                aa_column_alpha=None,aa_column_beta=1,count_column=2,v_alpha_column=None,j_alpha_column=None,v_beta_column=None,j_beta_column=None)

DTCRU.Train_VAE(accuracy_min=0.9, Load_Prev_Data=False)
distances_vae_seq = pdist(DTCRU.features, metric='euclidean')

DTCRU = DeepTCR_U('Clustering_Metrics')
#VAE_- Gene+Sequencs
DTCRU.Get_Data(directory='../Data/Sidhom',Load_Prev_Data=False,aggregate_by_aa=True,aa_column_beta=1,count_column=None,
               v_beta_column=7,d_beta_column=14,j_beta_column=21,p=p)
# DTCRU.Get_Data(directory='../Data/Dash/Traditional/Mouse',Load_Prev_Data=False,aggregate_by_aa=True,
#                aa_column_alpha=None,aa_column_beta=1,count_column=2,v_alpha_column=None,j_alpha_column=None,v_beta_column=5,j_beta_column=6)

DTCRU.Train_VAE(accuracy_min=0.9, Load_Prev_Data=False,seq_features_latent=False)
distances_vae_seq_gene = pdist(DTCRU.features, metric='euclidean')


#Hamming
distances_hamming = pdist(np.squeeze(DTCRU.X_Seq_beta, 1), metric='hamming')

#Kmer
kmer_features = kmer_search(DTCRU.beta_sequences)
distances_kmer = pdist(kmer_features, metric='euclidean')


p.close()
p.join()


distances_list = [distances_vae_seq,distances_vae_seq_gene,distances_vae_gene,distances_hamming,distances_kmer]
names = ['VAE-Seq','VAE-Seq-Gene','VAE-Gene','Hamming','K-mer']

dir_results = 'Length_Results'
if not os.path.exists(dir_results):
    os.makedirs(dir_results)

df_metrics = Assess_Performance_KNN(distances_list,names,DTCRU.label_id,dir_results)
Plot_Performance(df_metrics,dir_results,measurements=['AUC'])

SRCC = []
for n,distances in zip(names,distances_list):
    len_distance = pdist(np.sum(DTCRU.X_Seq_beta>0,-1))
    len_seq = np.sum(DTCRU.X_Seq_beta>0,-1)
    corr,_ = spearmanr(len_distance,distances)
    SRCC.append(corr)
    df = pd.DataFrame()
    df['D_len'] = len_distance.astype(int)
    df['D_features'] = distances
    plt.figure()
    sns.boxplot(x='D_len',y='D_features',data=df)
    plt.title(n)
    plt.savefig(os.path.join(dir_results,n+'_box.tif'))

df_out = pd.DataFrame()
df_out['Methods'] = names
df_out['SRCC'] = SRCC
df_out.to_csv(os.path.join(dir_results,'out.csv'),index=False)


for n,distances in zip(names,distances_list):
    plt.figure()
    sns.distplot(distances,hist=False,kde=True)
    plt.title(n)
    plt.savefig(os.path.join(dir_results,n+'_hist.tif'))


chi = list()
for n,d in zip(names,distances_list):
    chi.append(chi2_contingency(pd.crosstab(DTCRU.label_id, fcluster(linkage(d, 'ward'), 2, 'maxclust')).values)[0])

df_chi = pd.DataFrame()
df_chi['Methods'] = names
df_chi['Chi'] = chi
sns.barplot(data=df_chi,x='Methods',y='Chi')


df = Assess_Performance(DTCRU,distances_vae, distances_gan, distances_hamming, distances_kmer,dir_results,use_genes_label='use_genes_true')

