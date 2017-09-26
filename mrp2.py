from pulp import *
import data
import data2
import data3
import data4

bom = data4.data['bom']
materials = data4.data['materials']


def get_madeable_parts():
    result = {}
    for level, bill in bom.iteritems():
        tmp = level.split(".")
        depth = len(tmp)
        if depth > 1:
            tmp_level = ".".join(tmp[0:depth-1])
            part = bom[tmp_level][0][0]
            made_key = part + '_m'
            if made_key not in result:
                result[made_key] = {}
            result[made_key][level] = bill
    return result


def modify_bom(madeable_parts):
    for level, bill in bom.iteritems():
        parts = bill[0]
        for part in bill[0]:
            if part + '_m' in madeable_parts:
                parts.append(part + '_m')
        bill[0] = parts


def main():
    madeable_parts = get_madeable_parts()
    modify_bom(madeable_parts)
    print bom
    print madeable_parts
    madeable_part_lp_vars = {}
    sum_madeable_part_lp_vars = {}
    for part in madeable_parts:
        madeable_part_lp_vars[part] = LpVariable(part, lowBound=0, cat=LpInteger)
        sum_madeable_part_lp_vars[part] = []

    lp_part_vars = {}

    for key, value in materials.iteritems():
        lp_part_vars[key] = []

    prob = LpProblem("Dong bo san pham", LpMaximize)
    sync_num = LpVariable("sync_num", lowBound=0, cat=LpInteger)

    # objective
    prob += sync_num

    # equality constraints
    for level, bill in bom.iteritems():
        parts = bill[0]
        quantity = bill[1]
        lp_vars = []
        for part in parts:
            lp_var = LpVariable(part + '_' + level,
                                lowBound=0,
                                cat=LpInteger if isinstance(quantity, int) else LpContinuous)
            if "_m" not in part:
                lp_part_vars[part].append(lp_var)
            else:
                sum_madeable_part_lp_vars[part].append(lp_var)
            lp_vars.append(lp_var)

        if len(level.split(".")) == 1:
            prob += lpSum(lp_vars) - sync_num == 0
        else:
            tmp = level.split(".")
            tmp_level = ".".join(tmp[0:len(tmp) - 1])
            tmp_part = bom[tmp_level][0][0]
            prob += lpSum(lp_vars) == quantity * madeable_part_lp_vars[tmp_part + "_m"]

    # inequality constraints
    for key, vars in lp_part_vars.iteritems():
        prob += lpSum(vars) <= materials[key]

    for key, vars in sum_madeable_part_lp_vars.iteritems():
        prob += lpSum(vars) - madeable_part_lp_vars[key] <= 0

    prob.solve()

    for var in prob.variables():
        print "%s=%d" % (var.name, var.varValue)

    print("Status:", LpStatus[prob.status])
    # print("Objective = ", value(prob.objective))


if __name__ == '__main__':
    main()
