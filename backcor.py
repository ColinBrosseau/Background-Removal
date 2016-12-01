import numpy as np

def backcor(n, y, order, threshold, fct='atq', mask=True):
    '''
    Background estimation by minimizing a non-quadratic cost function.
    
    [EST, COEFS, IT] = backcor(N, Y, ORDER, THRESHOLD, fcn=FUNCTION, index=True) computes an
    estimation EST of the background (aka. baseline) in a spectroscopic 
    signal Y with wavelength N.
    The background is estimated by a polynomial with order ORDER using a 
    cost-function FUNCTION with parameter THRESHOLD. FUNCTION can have the four
    following values:
        'sh'  - symmetric Huber function :  
            f(x) = { x^2  if abs(x) < THRESHOLD,
                   { 2*THRESHOLD*abs(x)-THRESHOLD^2  otherwise.
        'ah'  - asymmetric Huber function :  
            f(x) = { x^2  if x < THRESHOLD,
                   { 2*THRESHOLD*x-THRESHOLD^2  otherwise.
        'stq' - symmetric truncated quadratic :  
            f(x) = { x^2  if abs(x) < THRESHOLD,
                   { THRESHOLD^2  otherwise.
        'atq' - asymmetric truncated quadratic :  
            f(x) = { x^2  if x < THRESHOLD,
                   { THRESHOLD^2  otherwise.
    mask relate to a mask to put on point for for calculation of cost function
          if True, all elements are valid
          else for exemple [0, 0, 1, 1, 1, 0, 0] only elements 2-4 are valid

   COEFS returns the ORDER+1 vector of the estimated polynomial coefficients.
   IT returns the number of iterations.

    For more informations, see:
        - V. Mazet, C. Carteret, D. Brie, J. Idier, B. Humbert. 
            Chemom. Intell. Lab. Syst. 76 (2), 2005.
        - V. Mazet, D. Brie, J. Idier. Proceedings of EUSIPCO, 
            pp. 305-308, 2004.
        - V. Mazet. PhD Thesis, University Henri Poincaré Nancy 1, 2005.
 
    22-June-2004, Revised 19-June-2006, Revised 30-April-2010,
    Revised 12-November-2012 (thanks E.H.M. Ferreira!)
    Comments and questions to: vincent.mazet@unistra.fr.
    13-september-2016 Translation to Python (Colin-N. Brosseau)
    1-december-2016 Add mask option (Colin-N. Brosseau)
    '''
# ??? To be done in Python
    # Check arguments
#    if nargin < 2, error('backcor:NotEnoughInputArguments','Not enough input arguments'); end;
#    if nargin < 5, [z,a,it,order,threshold,fct] = backcorgui(n,y); return; end; # delete this line if you do not need GUI
#    if ~isequal(fct,'sh') && ~isequal(fct,'ah') && ~isequal(fct,'stq') && ~isequal(fct,'atq'),
#    error('backcor:UnknownFunction','Unknown function.');
#    end;

    try:
        if mask == True:
            mask = np.ones((len(n), 1), dtype=bool)
    except:
        pass

    #save n for output of background calculation at the end on the full x-axis
    n_initial = n
    
    #only keep valid points
    I = np.where(mask)[0]
    n = n[I]
    y = y[I]

    # Rescaling
    N = len(n)
    i =  np.argsort(n)
    n = n[i]
    y = y[i]
    mask = mask[i]
    
    maxy = max(y)
    dely = (maxy-min(y))/2
    rescale_offset = -n[-1]
    rescale_factor = 2 / (n[-1]-n[0]) 
    n = (n+rescale_offset) * rescale_factor + 1
    y = (y-maxy)/dely + 1
    threshold /= dely

    # Initial shape
    if len(np.shape(y)) == 1:  # row array
        shape = 'row'
    else:
        shape = 'column'

    # Make column vectors
    N = len(n)
    n = n.reshape((N, 1))
    y = y.reshape((N, 1))
            
    # Vandermonde matrix
    p = np.arange(order+1)
    T = np.tile(n, (1, order+1)) ** np.tile(p, (N, 1))
    Tinv = np.dot(np.linalg.pinv( np.dot(T.T,T) ), T.T)
    
    # Initialisation (least-squares estimation)
    a = np.dot(Tinv, y)
    z = np.dot(T, a)

    # Other variables
    alpha = 0.99 * 1/2      # Scale parameter alpha
    it = 0                  # Iteration number
    zp = np.ones((N, 1))    # Previous estimation

    # LEGEND
    while sum((z-zp)**2)/sum(zp**2) > 1e-9:

        it = it + 1         # Iteration number
        zp = z              # Previous estimation
        res = y - z         # Residual

        # Estimate d
        if fct == 'sh':
            #print('sh')
            a1 = (abs(res)<threshold).astype(int)
            a2 = (res<=-threshold).astype(int)
            a3 = (res>=threshold).astype(int)
            d = (res*(2*alpha-1)) * a1 + (-alpha*2*threshold-res) * a2 + (alpha*2*threshold-res) * a3
        elif fct == 'ah':
            #print('ah')
            a1 = (res<threshold).astype(int)
            a2 = (res>=threshold).astype(int)
            d = (res*(2*alpha-1)) * a1 + (alpha*2*threshold-res) * a2
        elif fct == 'stq':
            #print('stq')
            a1 = (abs(res)<threshold).astype(int)
            a2 = (abs(res)>=threshold).astype(int)
            d = (res*(2*alpha-1)) * a1 - res * a2
        elif fct == 'atq':
            #print('atq')
            a1 = (res<threshold).astype(int)
            a2 = (res>=threshold).astype(int)
            d = (res*(2*alpha-1)) * a1 - res * a2

        # Estimate z
        a = np.dot(Tinv, (y+d))    # Polynomial coefficients a
        z = np.dot(T, a)           # Polynomial
   
    #back to original x-axis
    # Rescale 
    N = len(n_initial)
    i =  np.argsort(n_initial)
    n_initial = n_initial[i]
    n_initial = (n_initial+rescale_offset) * rescale_factor + 1
    # Make column vectors
    n_initial = n_initial.reshape((N, 1))
    # Vandermonde matrix
    p = np.arange(order+1)
    T = np.tile(n_initial, (1, order+1)) ** np.tile(p, (N, 1))
    z = np.dot(T, a)           # Polynomial
    # Rescaling back to original
    j =  np.argsort(i)
    z = (z[j]-1)*dely + maxy 
    
    # Put back on initial shape
    if shape == 'row':
        z = np.squeeze(z)

    #z  Background
    #a  Polynomial coefficient
    #it Iteration number
    return z, a, it
