import pulp

I = {'H', 'S1', 'S2', 'S3', 'S4'}
K = {'GJ19', 'HM22', 'CP31', 'P68'}

p = {('S1', 'GJ19'): 10.08, ('S2', 'GJ19'): 11.28, ('S3', 'GJ19'): 8.52,
     ('S1', 'HM22'): 3.92, ('S2', 'HM22'): 5.00, ('S3', 'HM22'): 4.92, ('S4', 'HM22'): 3.96,
     ('S1', 'CP31'): 12.60, ('S2', 'CP31'): 15.96, ('S3', 'CP31'): 16.66,
     ('S1', 'P68'): 6.78, ('S2', 'P68'): 5.46, ('S3', 'P68'): 7.62, ('S4', 'P68'): 7.62}

d = {('H', 'S1'): 14.3, ('H', 'S2'): 6.8, ('H', 'S3'): 4.7, ('H', 'S4'): 9.5,
     ('S2', 'S1'): 12.2, ('S2', 'S4'): 11.3,
     ('S3', 'S1'): 9.9, ('S3', 'S2'): 5.8, ('S3', 'S4'): 12.9,
     ('S4', 'S1'): 22.4,
     ('S1', 'H'): 14.6, ('S2', 'H'): 7.9, ('S3', 'H'): 5.5, ('S4', 'H'): 10.8}

c = 0.30

x_keys = set(d.keys())
y_keys = set(p.keys())

# Define the model
mdl = pulp.LpProblem('grabbro', sense=pulp.LpMinimize)

# Add variables
x = pulp.LpVariable.dicts(indices=x_keys, cat=pulp.LpBinary, name='x')
y = pulp.LpVariable.dicts(indices=y_keys, cat=pulp.LpBinary, name='y')

# Add Constraints
mdl.addConstraint(sum(x.get(('H', j), 0) for j in I) == 1, name='c1')
mdl.addConstraint(sum(x.get((i, 'H'), 0) for i in I) == 1, name='c2')
for l in I:
    mdl.addConstraint(sum(x.get((i, l), 0) for i in I) == sum(x.get((l, j), 0) for j in I), name=f'c3_{l}')
for k in K:
    mdl.addConstraint(sum(y.get((i, k), 0) for i in I) == 1, name=f'c4_{k}')
for j, k in y_keys:
    mdl.addConstraint(y.get((j,k), 0) <= sum(x.get((i, j), 0) for i in I), name=f'c5_{k},{j}')

# Set the objective function
transit_cost = c * sum(d[ij] * x[ij] for ij in x_keys)
purchasing_cost = sum(p[ik] * y[ik] for ik in y_keys)
mdl.setObjective(transit_cost + purchasing_cost)

# Optimize
mdl.solve()

# Retrieve the solution
status_code = mdl.solve()
status = pulp.LpStatus[status_code]
if status == 'Optimal':
    print(f'Optimal solution found!')
    x_sol = {key: v.value() for key, v in x.items() if v.value() > 0.5}
    print(f'Route: {x_sol}')
    print(f'Transit Distance: {transit_cost.value() / c}')
    print(f'Transit Cost: {transit_cost.value()}')
    print(f'Purchasing Cost: {purchasing_cost.value()}')
    print(f'Total Cost: {transit_cost.value() + purchasing_cost.value()}')
else:
    print(f'Model is not optimal. Status: {status}')
