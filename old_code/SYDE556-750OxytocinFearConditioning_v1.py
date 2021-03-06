# Peter Duggins
# SYDE 556/750
# April 2016
# Final Project - Oxytocin and Fear Conditioning

import nengo
import nengo_gui
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams['lines.linewidth'] = 1
plt.rcParams['font.size'] = 20

#ensemble parameters
stim_N=50 #neurons for stimulus populations
stim_dim=1 #dimensionality of CS and context
ens_N=50 #neurons for ensembles
ens_dim=1 #dimensions for ensembles
stim_syn=0.01 #synaptic time constant of stimuli to populations
ens_syn=0.01 #synaptic time constant between ensembles
learn_rate = 5e-4 #first order conditioning learning rate
learn_syn=0.02

#stimuli
def US_function(t):
    if 0.8<t<1: return 1
    if 1.8<t<2: return 1
    if 2.8<t<3: return 1
    return 0

def CS_function(t):
    if 0.7<t<1: return 1
    if 1.7<t<2: return 1
    if 2.7<t<3: return 1
    return 0

#model definition
model=nengo.Network(label='Oxytocin Fear Conditioning')
with model:

	#STIMULI ####################################

	stim_US=nengo.Node(output=US_function)
	stim_CS=nengo.Node(output=CS_function)
	stop_learn = nengo.Node([0])

	#ENSEMBLES ####################################

	#PAG subpopulations
	US=nengo.Ensemble(stim_N,1) #US is scalar valued
	U=nengo.Ensemble(ens_N,ens_dim) #intermediary
	Error=nengo.Ensemble(ens_N,ens_dim) #excited by stim_US through U, recurrent inhibition to dampen

	#Amygdala subpopulations
	LA=nengo.Ensemble(ens_N,ens_dim) #lateral amygdala, learns associations
	BA=nengo.Ensemble(ens_N,ens_dim) #basolateral amygdala, named BL in Carter
	CeM=nengo.Ensemble(ens_N,ens_dim) #medial central amygdala, outputs fear responses

	#Cortex subpopulations
	CS=nengo.Ensemble(stim_N,stim_dim) #excited by stim_CS through C

	#Hippocampus subpopulations
	C=nengo.Ensemble(stim_N,stim_dim) #intermediary

	#CONNECTIONS ####################################

	#Connections between stimuli and ensembles
	nengo.Connection(stim_US,US,synapse=stim_syn)
	nengo.Connection(stim_CS,CS,synapse=stim_syn)

	#Feedforward connections between ensembles
	nengo.Connection(CS,C,synapse=ens_syn)
	nengo.Connection(U,Error,synapse=ens_syn)
	nengo.Connection(US,U,synapse=ens_syn)
	nengo.Connection(LA,BA,synapse=ens_syn)
	nengo.Connection(BA,CeM,synapse=ens_syn)
	
	#recurrent inhibition on R
# 	Rinhib=nengo.Ensemble(ens_N,ens_dim)
#  	nengo.Connection(R,Rinhib,transform=1,synapse=0.01)
#  	nengo.Connection(Rinhib,R,transform=-1,synapse=0.01)

	#Learned connections and Error calculation
	conditioning = nengo.Connection(C,LA,function=lambda x: [0]*ens_dim,synapse=learn_syn)
	conditioning.learning_rule_type = nengo.PES(learning_rate=learn_rate)
	nengo.Connection(Error, conditioning.learning_rule,transform=-1)
	nengo.Connection(stop_learn, Error.neurons, transform=-10*np.ones((ens_N, ens_dim)))
	nengo.Connection(CeM, Error,transform=-0.5)
    
	#PROBES ####################################
	US_probe=nengo.Probe(US, synapse=0.01)
	CS_probe=nengo.Probe(CS, synapse=0.01)
	CeM_probe = nengo.Probe(CeM, synapse=0.01)