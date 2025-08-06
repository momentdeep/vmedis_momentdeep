import numpy as np

def tm_fuction(df, N_predict):

    X = list(map(lambda x: x, range(0, len(df))))
    Y = df['Jumlah']
    N=df.shape[0]

    df['X'] = X
    df['X^2'] = list(map(lambda x: x**2, range(0, len(df))))
    df['XY']=list(map(lambda x,y: x*y, X,Y))
    print(df)

    A = np.array([[len(Y),sum(X)],[sum(X), df['X^2'].sum()]])
    B = np.array([sum(Y), df['XY'].sum()])

    # Solve: AX = B
    X = np.linalg.solve(A, B)
    print(X)
    print(f"x = {X[0]:.4f}")
    print(f"y = {X[1]:.4f}")

    y_est=[]
    for i in range(0,N_predict):
        x_in=N+i
        y_est.append(round(X[0]+X[1]*x_in))
        
    return y_est