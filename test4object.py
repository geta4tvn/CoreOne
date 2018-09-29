class a:
    def __init__(self,alpha, beta,tria, tessera, pente):
        self.alpha=alpha
        self.beta=beta
        self.tria=tria
        self.tessera=tessera
        self.pente=pente


jim=a(1,2,'tria',4,5)


def synartisi(a):
    print(a.alpha)
    a.alpha=900
    print(a.tria)

print('1st call')
synartisi(jim)

print('2nd call')
synartisi(jim)

