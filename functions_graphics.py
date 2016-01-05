import os
import matplotlib.pyplot as plt
import numpy as np

# Global figure variable
# This is to make sure each plot is drawn in a new window, no matter which plotting methods are used
n_fig = 1

def basic_xy(x,y,color='b'):
    
    global n_fig
    figure = plt.figure(n_fig)
    figure.add_subplot(1, 1, 1, axisbg='1') # Change background color here
    plt.gca().set_aspect('equal')  
    plt.plot(x,y,color)
    plt.show()
    
#    time.sleep(5)
    n_fig += 1

def body_wake_plot(Swimmers):
    
    global n_fig
    figure = plt.figure(n_fig)
    plt.clf()
    figure.add_subplot(1, 1, 1, axisbg='1') # Change background color here
    plt.gca().set_aspect('equal')
    maxpercentile = 95 # For truncating outliers
    
    # Gather circulations of all swimmers into a color array
    color = []
    for Swim in Swimmers:
        Swim.n_color = len(Swim.Wake.gamma[1:-1])
        color = np.append(color, Swim.Wake.gamma[1:-1])
        Swim.i_color = len(color)-Swim.n_color
    
    # Make color map based on vorticity
    # Take a look at positive and negative circulations separately
    if np.min(color) < 0: # Check if negative circulations exist (in case of short simulations)
        # Truncate any negative outliers
        color[color < np.percentile(color[color < 0], 100-maxpercentile)] = np.percentile(color[color < 0], 100-maxpercentile)
        # Normalize negative circulations to [-1,0)
        color[color < 0] = -color[color < 0]/np.min(color)
    if np.max(color) > 0: # Check if positive circulations exist (in case of short simulations)
        # Truncate any positive outliers
        color[color > np.percentile(color[color > 0], maxpercentile)] = np.percentile(color[color > 0], maxpercentile)
        # Normalize positive circulations to (0,1]
        color[color > 0] = color[color > 0]/np.max(color)
        
    for Swim in Swimmers:
        # Extract color map for the individual Swim
        c = color[Swim.i_color:Swim.i_color+Swim.n_color]
        # Scatter plot of wake points with red-white-blue colormap, as well as body outline and edge panel segment
        plt.scatter(Swim.Wake.x[1:-1], Swim.Wake.z[1:-1], s=30, c=c, edgecolors='none', cmap=plt.get_cmap('bwr_r'))
        plt.plot(Swim.Body.AF.x, Swim.Body.AF.z, 'k')
        plt.plot(Swim.Edge.x, Swim.Edge.z, 'g')
        plt.show()
    
    n_fig += 1
    
def cp_plot(Swimmers, i, SW_PLOT_FIG):
    
    global n_fig
    if SW_PLOT_FIG:
        cp_scale = 1000
        figure = plt.figure(1)
        figure.add_subplot(1, 1, 1, axisbg='1') # Change background color here
#        plt.gca().set_aspect('equal')
        plt.gca().invert_yaxis()
        maxpercentile = 95 # For truncating outliers
        
        if (i > 1):
            # Gather circulations of all swimmers into a color array
            color = []
            for Swim in Swimmers:
                Swim.n_color = len(Swim.Wake.gamma[1:i])
                color = np.append(color, Swim.Wake.gamma[1:i])
                Swim.i_color = len(color)-Swim.n_color
            
            # Make color map based on vorticity
            # Take a look at positive and negative circulations separately
            if np.min(color) < 0: # Check if negative circulations exist (in case of short simulations)
                # Truncate any negative outliers
                color[color < np.percentile(color[color < 0], 100-maxpercentile)] = np.percentile(color[color < 0], 100-maxpercentile)
                # Normalize negative circulations to [-1,0)
                color[color < 0] = -color[color < 0]/np.min(color)
            if np.max(color) > 0: # Check if positive circulations exist (in case of short simulations)
                # Truncate any positive outliers
                color[color > np.percentile(color[color > 0], maxpercentile)] = np.percentile(color[color > 0], maxpercentile)
                # Normalize positive circulations to (0,1]
                color[color > 0] = color[color > 0]/np.max(color)
            
        for Swim in Swimmers:
#            if (i > 1):
#                # Extract color map for the individual Swim
#                c = color[Swim.i_color:Swim.i_color+Swim.n_color]
#                # Scatter plot of wake points with red-white-blue colormap, as well as body outline and edge panel segment
#    #            for idx in xrange(i):
#                plt.scatter(Swim.Wake.x[1:i], Swim.Wake.z[1:i], s=30, c=c, edgecolors='none', cmap=plt.get_cmap('bwr_r'))
#    #            plt.scatter(Swim.Wake.x[1:-1], Swim.Wake.z[1:-1], s=30, c=c, edgecolors='none', cmap=plt.get_cmap('bwr_r'))
#            plt.plot(Swim.Body.AF.x, Swim.Body.AF.z, 'k')
#            plt.plot(Swim.Edge.x, Swim.Edge.z, 'g')
            plt.plot(Swim.Body.BF.x_col[:Swim.Body.N/2], Swim.Body.cp[:Swim.Body.N/2]/cp_scale, 'g')
            plt.plot(Swim.Body.BF.x_col[Swim.Body.N/2:], Swim.Body.cp[Swim.Body.N/2:]/cp_scale, 'b')

#        plt.axis([np.min(Swim.Body.AF.x)-0.01, np.min(Swim.Body.AF.x)+0.13, -0.06, 0.06])
        plt.axis([np.min(Swim.Body.BF.x)+0.108, np.min(Swim.Body.BF.x)+0.13, -0.2, 0.1])
        plt.xlabel('$X$ $[m]$', fontsize=14)
        plt.ylabel('$Z$ $[m]$ $or$ $C_p$ x$10^{-2}$ $[-]$', fontsize=14)
        
        figure.savefig('./movies/%05i.png' % (n_fig), format='png')
            
        plt.clf()
    
    n_fig += 1
    
def drag_vs_period(Body,RHO,t):
    
    global n_fig
    figure = plt.figure(n_fig)
    figure.add_subplot(1, 1, 1, axisbg='1') # Change background color here
    plt.xlabel('tau')
    plt.ylabel('Coefficent of drag')
    
    plt.plot(t[4:]*Body.F, -Body.drag[3:]/(0.5*RHO*Body.V0**2), 'b')
    
    n_fig += 1
    
def lift_vs_period(Body,RHO,t):
    
    global n_fig
    figure = plt.figure(n_fig)
    figure.add_subplot(1, 1, 1, axisbg='1') # Change background color here
    plt.xlabel('tau')
    plt.ylabel('Coefficent of lift')
    
#    plt.plot(t[4:]*Body.F, -Body.lift[3:]/(0.5*RHO*Body.V0**2), 'g')
    plt.plot(t[4:], Body.Cl[3:] * (0.5 * RHO * np.abs(Body.V0)**2 * 0.1 * 1), 'g')
    
    n_fig += 1
    
#def plot_n_go(Edge, Body, Solid, V0, T, HEAVE):
def plot_n_go(Swimmers, V0, T, HEAVE, i, SW_PLOT_FIG):
    global n_fig
    
    if SW_PLOT_FIG:
        figure = plt.figure(1)
        figure.add_subplot(1, 1, 1, axisbg='1') # Change background color here
        figure.set_size_inches(16, 9)
        plt.gca().set_aspect('equal')
        plt.tick_params(labelsize=28)
        plt.xticks(np.arange(-15.00, 15.00, 0.20))
        maxpercentile = 95 # For truncating outliers
        
        if (i > 1):
            # Gather circulations of all swimmers into a color array
            color = []
            for Swim in Swimmers:
                Swim.n_color = len(Swim.Wake.gamma[1:i])
                color = np.append(color, Swim.Wake.gamma[1:i])
                Swim.i_color = len(color)-Swim.n_color
            
            # Make color map based on vorticity
            # Take a look at positive and negative circulations separately
            if np.min(color) < 0: # Check if negative circulations exist (in case of short simulations)
                # Truncate any negative outliers
                color[color < np.percentile(color[color < 0], 100-maxpercentile)] = np.percentile(color[color < 0], 100-maxpercentile)
                # Normalize negative circulations to [-1,0)
                color[color < 0] = -color[color < 0]/np.min(color)
            if np.max(color) > 0: # Check if positive circulations exist (in case of short simulations)
                # Truncate any positive outliers
                color[color > np.percentile(color[color > 0], maxpercentile)] = np.percentile(color[color > 0], maxpercentile)
                # Normalize positive circulations to (0,1]
                color[color > 0] = color[color > 0]/np.max(color)
            
        for Swim in Swimmers:
            if (i > 1):
                # Extract color map for the individual Swim
                c = color[Swim.i_color:Swim.i_color+Swim.n_color]
                # Scatter plot of wake points with red-white-blue colormap, as well as body outline and edge panel segment
    #            for idx in xrange(i):
                plt.scatter(Swim.Wake.x[1:i], Swim.Wake.z[1:i], s=30, c=c, edgecolors='none', cmap=plt.get_cmap('bwr_r'))
    #            plt.scatter(Swim.Wake.x[1:-1], Swim.Wake.z[1:-1], s=30, c=c, edgecolors='none', cmap=plt.get_cmap('bwr_r'))
            plt.plot(Swim.Body.AF.x, Swim.Body.AF.z, 'k')
            plt.plot(Swim.Edge.x, Swim.Edge.z, 'g')
    
        # Determine if the output directory exists. If not, create the directory.
        if not os.path.exists('./movies'):
            os.makedirs('./movies')
        
        plt.axis([np.min(Swim.Body.AF.x)-0.05, np.min(Swim.Body.AF.x)+1.75, -0.5, 0.5])
#        plt.axis([np.min(Swim.Body.AF.x)-0.75, np.min(Swim.Body.AF.x)+25.5, -7.5, 7.5])
#        plt.axis([np.min(Swim.Body.AF.x)-0.05, np.min(Swim.Body.AF.x)+0.75, -0.2, 0.2])
        plt.xlabel('$X$ $[m]$', fontsize=28)
        plt.ylabel('$Z$ $[m]$', fontsize=28)
        
        plt.axes([0.13, 0.677, 0.2, 0.2])
        plt.gca().set_aspect('equal')
        plt.gca().axes.get_xaxis().set_visible(False)
        plt.gca().axes.get_yaxis().set_visible(False)
#        plt.axis([np.min(Swim.Body.AF.x)+0.06, np.min(Swim.Body.AF.x)+0.16, -0.03, 0.03])
        plt.axis([np.min(Swim.Body.AF.x)-0.04, np.min(Swim.Body.AF.x)+0.14, -0.05, 0.05])
        for Swim in Swimmers:
            if (i > 1):
                # Extract color map for the individual Swim
                c = color[Swim.i_color:Swim.i_color+Swim.n_color]
                # Scatter plot of wake points with red-white-blue colormap, as well as body outline and edge panel segment
                plt.scatter(Swim.Wake.x[1:i], Swim.Wake.z[1:i], s=30, c=c, edgecolors='none', cmap=plt.get_cmap('bwr_r'))
            plt.plot(Swim.Body.AF.x, Swim.Body.AF.z, 'k')
            plt.plot(Swim.Edge.x, Swim.Edge.z, 'g')
            
        figure.savefig('./movies/%05i.png' % (n_fig), format='png')
        
        plt.clf()
    
    n_fig += 1  

def body_plot(Edge, Body):
    global n_fig
    
    # Determine if the output directory exists. If not, create the directory.
    if not os.path.exists('./movies'):
        os.makedirs('./movies')
        
    figure = plt.figure(1)
    figure.add_subplot(1, 1, 1, axisbg='1') # Change background color here
    plt.gca().set_aspect('equal')
    plt.gca().axes.get_xaxis().set_visible(False)
    plt.gca().axes.get_yaxis().set_visible(False)
    plt.box(on='off')
    
    
#    plt.plot(Body.AF.x_col[:Body.N/2], Body.cp[:Body.N/2]/100, 'g')
#    plt.plot(Body.AF.x_col[Body.N/2:], Body.cp[Body.N/2:]/100, 'b')
    plt.plot(Body.AF.x, Body.AF.z, 'k')

    plt.xlim((np.min(Body.AF.x)-0.125, np.min(Body.AF.x)+0.125))
    plt.plot(Edge.x, Edge.z, 'g')
    plt.ylim((-0.05, 0.05))
    
    figure.savefig('./movies/%05i.png' % (n_fig), format='png')
    plt.clf()
    
    n_fig += 1

def body(x,y,color='b'):
    figure = plt.figure(2)
    figure.add_subplot(1, 1, 1, axisbg='1') # Change background color here
    plt.gca().set_aspect('equal')  
    plt.plot(x,y,color)
    plt.xlim((np.min(x)-0.02, np.min(x)+0.22))
    plt.ylim((-0.05, 0.05))
    plt.show()
