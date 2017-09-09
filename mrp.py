from pulp import *
import data
import data2
import data3

bom = data2.bom
materials = data2.materials

# needed number of each part for the level that part appears
# for example ['A_1','A_2','B_1',...] is number of A in level 1,2 and number of B in level 1
lp_vars = []

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
                lp_var = LpVariable(name=part + '_' + level,
                                    lowBound=0,
                                    upBound=num,
                                    cat=LpInteger if isinstance(bill[1], int) else LpContinuous)
                lp_vars.append(lp_var)
                objective.append(0)
    # objective will be finding maximize of produced products, a number called K
    objective.append(1)


def build_ub():
    for part, num in materials.iteritems():
        row = []
        for var in lp_vars:
            if part == var.name.split('_')[0]:
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

        for var in lp_vars:
            if var.name.split('_')[0] in options and var.name.split('_')[1] == level:
                row.append(1)
            else:
                row.append(0)

        row.append(-coef)  # coef for K
        A_eq.append(row)
        B_eq.append(0)


def build_bounds():
    for var in lp_vars:
        bounds.append((0, materials[var.name.split('_')[0]]))
    bounds.append((0, None))  # bounds for K


def main():
    prob = LpProblem("Dong bo san pham", LpMaximize)
    get_variables()
    build_eq()
    build_ub()
    build_bounds()

    lp_vars.append(LpVariable('K', 0, cat=LpInteger))
    num_of_vars = len(lp_vars)

    prob += lpSum([objective[i] * lp_vars[i] for i in xrange(num_of_vars)])

    for i in xrange(len(A_eq)):
        prob += lpSum([A_eq[i][j] * lp_vars[j] for j in xrange(num_of_vars)]) == B_eq[i]

    for i in xrange(len(A_ub)):
        prob += lpSum([A_ub[i][j] * lp_vars[j] for j in xrange(num_of_vars)]) <= B_ub[i]

    prob.solve()

    # Solution
    for v in prob.variables():
        print v.name, "=", v.varValue

    print "objective=", value(prob.objective)


if __name__ == '__main__':
    main()
