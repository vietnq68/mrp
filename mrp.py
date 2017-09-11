from pulp import *
import data
import data2
import data3

bom = data2.data['bom']
materials = data2.data['materials']

# needed number of each part for the level that part appears
# for example ['A_1','A_2','B_1',...] is number of A in level 1,2 and number of B in level 1
lp_vars = []

# variables for Simplex problem
A_eq = []
B_eq = []
B_ineq = []
A_ineq = []
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


def get_objective():
    # objective will be finding maximize of produced products, a number called K
    for var in lp_vars:
        objective.append(0)
    objective.append(1)  # coef for K


def get_inequality_constraints():
    for part, num in materials.iteritems():
        row = []
        for var in lp_vars:
            row.append(1 if part == var.name.split('_') else 0)

        row.append(0)  # coef for K

        A_ineq.append(row)
        B_ineq.append(num)


def get_equality_constraints():
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


def main():
    prob = LpProblem("Dong bo san pham", LpMaximize)
    get_variables()
    get_objective()
    get_equality_constraints()
    get_inequality_constraints()

    lp_vars.append(LpVariable('K', 0, cat=LpInteger))
    num_of_vars = len(lp_vars)

    # objective
    prob += lpSum([objective[i] * lp_vars[i] for i in xrange(num_of_vars)])

    # equality constraints
    for i in xrange(len(A_eq)):
        prob += lpSum([A_eq[i][j] * lp_vars[j] for j in xrange(num_of_vars)]) == B_eq[i]

    # inequality constraints
    for i in xrange(len(A_ineq)):
        prob += lpSum([A_ineq[i][j] * lp_vars[j] for j in xrange(num_of_vars)]) <= B_ineq[i]

    prob.solve()

    # Solution
    materials_dict = {}
    for v in prob.variables():
        materials_dict[v.name] = v.varValue

    print "objective=", value(prob.objective)
    print materials_dict


if __name__ == '__main__':
    main()
