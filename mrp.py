from scipy.optimize import linprog
import data

bom = data.bom
materials = data.materials

# needed number of each part for the level that part appears
# for example ['A_1','A_2','B_1',...] is number of A in level 1,2 and number of B in level 1
variables = []

# variables for Simplex problem
# check: https://docs.scipy.org/doc/scipy-0.18.1/reference/generated/scipy.optimize.linprog.html
A_eq = []
B_eq = []
B_ub = []
A_ub = []
bounds = []
objective = []


def get_variables():
    for part, num in materials.iteritems():
        for level, bill in bom.iteritems():
            if part in bill[0]:
                variables.append(part + '_' + level)
                objective.append(0)
    # objective will be finding maximize of produced products, a number called K
    # it will be find minimum of -K
    objective.append(-1)


def build_ub():
    for part, num in materials.iteritems():
        row = []
        for var in variables:
            if part == var.split('_')[0]:
                row.append(1)
            else:
                row.append(0)

        row.append(0)  # coef for K
        A_ub.append(row)
        B_ub.append(num)


def build_eq():
    for level, bill in bom.iteritems():
        row = []
        coef = bill[1]
        options = bill[0]

        for var in variables:
            if var.split('_')[0] in options and var.split('_')[1] == level:
                row.append(1)
            else:
                row.append(0)

        row.append(-coef) # coef for K
        A_eq.append(row)
        B_eq.append(0)


def build_bounds():
    for var in variables:
        bounds.append((0, materials[var.split('_')[0]]))
    bounds.append((0, None)) # bounds for K

def main():
    print 'Starting the optimization ...'
    get_variables()
    build_eq()
    build_ub()
    build_bounds()

    print 'Variables: %s' % (variables)

    res = linprog(objective, A_eq=A_eq, b_eq=B_eq, A_ub=A_ub, b_ub=B_ub, bounds=bounds, options={"disp": True})

    optimized = dict(zip(variables, res.x))

    print '=============================='
    print 'BEST NUMBER: %d' % (-res.fun)
    print '=============================='

    for level, bill in bom.iteritems():
        options = bill[0]
        suggested = [optimized[option + '_' + level] for option in options]
        tmp = dict(zip(options, suggested))
        print 'Level: %s    %s' % (level, tmp)


if __name__ == '__main__':
    main()
