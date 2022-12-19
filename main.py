import pyomo.environ as pyEnv
import pyomo.opt
import random

def random_matrix(l):
    m = []
    for i in range(0, l):
        n = []
        for j in range(0, l):
            if i == j:
                n.append(9999)
            else:
                n.append(random.randint(0, 70))
        m.append(n)

    return m


file = open('17.txt')
lines = file.readlines()
file.close()
cost_matrix = []
#cost_matrix = random_matrix(31)

for i in range(len(lines)):
    aux = lines[i][:-1].split('\t')
    aux = [int(i) for i in aux if i != '']
    cost_matrix.append(aux)


n = len(cost_matrix)

# Model
model = pyEnv.ConcreteModel()

# Indexes for the cities
model.M = pyEnv.RangeSet(n)
model.N = pyEnv.RangeSet(n)

# Index for the dummy variable u
model.U = pyEnv.RangeSet(2, n)

# Decision variables xij
model.x = pyEnv.Var(model.N, model.M, within=pyEnv.Binary)

# Dummy variable ui
model.u = pyEnv.Var(model.N, within=pyEnv.NonNegativeIntegers, bounds=(0, n - 1))

# Cost Matrix cij
model.c = pyEnv.Param(model.N, model.M, initialize=lambda model, i, j: cost_matrix[i - 1][j - 1])


def obj_func(model):
    return sum(model.x[i, j] * model.c[i, j] for i in model.N for j in model.M)


model.objective = pyEnv.Objective(rule=obj_func, sense=pyEnv.minimize)


def rule_const1(model, M):
    return sum(model.x[i, M] for i in model.N if i != M) == 1


model.const1 = pyEnv.Constraint(model.M, rule=rule_const1)


def rule_const2(model, N):
    return sum(model.x[N, j] for j in model.M if j != N) == 1


model.rest2 = pyEnv.Constraint(model.N, rule=rule_const2)


def rule_const3(model, i, j):
    if i != j:
        return model.u[i] - model.u[j] + model.x[i, j] * n <= n - 1
    else:
        # Yeah, this else doesn't say anything
        return model.u[i] - model.u[i] == 0


model.rest3 = pyEnv.Constraint(model.U, model.N, rule=rule_const3)

# Prints the entire model


# Solves
solver = pyomo.opt.SolverFactory('cplex')
result = solver.solve(model, tee='False')

# Prints the results
print(result)

custo = 0

l = list(model.x.keys())
for i in l:
    if model.x[i]() != 0:
        print(i, '--', model.x[i]())
        custo += cost_matrix[i[0] - 1][i[1] - 1]
print(custo)
