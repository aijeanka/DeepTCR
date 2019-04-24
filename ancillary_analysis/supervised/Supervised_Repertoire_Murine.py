from DeepTCR.DeepTCR import DeepTCR_SS, DeepTCR_WF

folds = 100
LOO = 4
epochs_min = 50
size_of_net = 'medium'

#Train Sequence Classifier
DTCR_SS = DeepTCR_SS('Rudqvist')
DTCR_SS.Get_Data(directory='../../Data/Rudqvist',Load_Prev_Data=False,
               aa_column_beta=1,count_column=2,v_beta_column=7,d_beta_column=14,j_beta_column=21)

DTCR_SS.Monte_Carlo_CrossVal(folds=folds,test_size=0.25)
DTCR_SS.AUC_Curve()

#Train Repertoire Classifier without on-graph clustering
DTCR_WF = DeepTCR_WF('Rudqvist')
DTCR_WF.Get_Data(directory='../../Data/Rudqvist',Load_Prev_Data=False,
               aa_column_beta=1,count_column=2,v_beta_column=7,d_beta_column=14,j_beta_column=21)

DTCR_WF.Monte_Carlo_CrossVal(folds=folds,LOO=LOO,epochs_min=epochs_min)
DTCR_WF.AUC_Curve()

#Train Repertoire Classifier with on-graph clustering
DTCR_WF.Monte_Carlo_CrossVal(folds=folds,LOO=LOO,on_graph_clustering=True,epochs_min=epochs_min)
DTCR_WF.AUC_Curve()

#Visualize Latent Space
DTCR_WF.UMAP_Plot(by_class=True,freq_weight=True,show_legend=True,scale=5000,Load_Prev_Data=False,
                  alpha=0.5)

